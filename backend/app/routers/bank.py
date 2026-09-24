import hashlib
import time
import uuid
from typing import Optional

import psycopg2.extras
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import FRONTEND_BASE_URL
from app.database import get_db_cursor
from app.pdf_utils import PDF_DIR, generate_yield_certificate_pdf
from app.routers.auth import hash_password, verify_password
from app.schemas import (
    BankFarmerProfileResponse,
    BankFarmerSearchResponse,
    BankLoginRequest,
    BankLoginResponse,
    BankRegisterRequest,
    BankRegisterResponse,
    CertificateGenerateRequest,
    CertificateGenerateResponse,
    CertificateVerifyResponse,
    ClaimVerifyRequest,
    ClaimVerifyResponse,
    BankOverviewResponse,
    LoanScoreRequest,
    LoanScoreResponse,
    PortfolioResponse,
)
from app.weather import fetch_historical_weather_for_date

router = APIRouter(prefix="/api/bank", tags=["bank"])

LOW_RISK_CROPS = {"wheat", "rice", "maize"}
MEDIUM_RISK_CROPS = {"onion", "tomato"}
HIGH_RISK_CROPS = {"cotton", "sugarcane"}

LOAN_BASE_PER_ACRE = {"Low": 100000, "Medium": 60000, "High": 30000}

FLOOD_RAIN_THRESHOLD_MM = 40.0
DROUGHT_RAIN_THRESHOLD_MM = 2.0
FROST_TEMP_THRESHOLD_C = 5.0

PORTFOLIO_CACHE_TTL_SECONDS = 6 * 60 * 60
_portfolio_cache: dict = {}


def portfolio_risk_level(health_zone, alert_count, has_yield) -> str:
    if health_zone in (None, "Red") or alert_count >= 2 or not has_yield:
        return "HIGH"
    if health_zone == "Yellow" or alert_count == 1:
        return "MEDIUM"
    return "LOW"


def evaluate_claim(reason: str, weather: dict) -> tuple:
    weather_date = weather.get("date")

    if reason == "flood":
        rainfall = weather.get("rainfall_mm")
        if rainfall is None:
            return (
                "INCONCLUSIVE",
                "Weather data for the claim date could not be retrieved, so this flood claim "
                "could not be checked against rainfall records.",
            )
        if rainfall >= FLOOD_RAIN_THRESHOLD_MM:
            return (
                "VALIDATED",
                f"{rainfall} mm of rain was recorded on {weather_date}, which supports a "
                "flood / excess-rain claim.",
            )
        return (
            "SUSPICIOUS",
            f"Only {rainfall} mm of rain was recorded on {weather_date}, which does not "
            "support a flood claim.",
        )

    if reason == "drought":
        rainfall = weather.get("rainfall_mm")
        if rainfall is None:
            return (
                "INCONCLUSIVE",
                "Weather data for the claim date could not be retrieved, so this drought "
                "claim could not be checked against rainfall records.",
            )
        if rainfall <= DROUGHT_RAIN_THRESHOLD_MM:
            return (
                "VALIDATED",
                f"Only {rainfall} mm of rain was recorded on {weather_date}, consistent with "
                "dry / drought conditions.",
            )
        return (
            "SUSPICIOUS",
            f"{rainfall} mm of rain was recorded on {weather_date}, which does not support a "
            "drought claim.",
        )

    if reason == "frost":
        temp_min = weather.get("temp_min_c")
        if temp_min is None:
            return (
                "INCONCLUSIVE",
                "Weather data for the claim date could not be retrieved, so this frost claim "
                "could not be checked against temperature records.",
            )
        if temp_min < FROST_TEMP_THRESHOLD_C:
            return (
                "VALIDATED",
                f"Minimum temperature on {weather_date} was {temp_min} deg C, below the frost "
                f"threshold of {FROST_TEMP_THRESHOLD_C} deg C.",
            )
        return (
            "SUSPICIOUS",
            f"Minimum temperature on {weather_date} was {temp_min} deg C, which does not "
            "support a frost claim.",
        )

    if reason == "pest":
        return (
            "INCONCLUSIVE",
            "Pest damage cannot be verified from weather data. This claim is flagged for "
            "manual field inspection.",
        )

    return (
        "INCONCLUSIVE",
        f"{reason.title()} claims cannot be verified from weather records alone. This claim "
        "is flagged for manual review.",
    )


def weather_risk_text(alert_count: int) -> str:
    if alert_count == 0:
        return "Low risk — no weather alerts recorded for this farmer"
    if alert_count == 1:
        return "Moderate risk — 1 active weather alert recorded for this farmer"
    return f"High risk — {alert_count} active weather alerts recorded for this farmer"


def soil_health_points(zone):
    if zone == "Green":
        return 25, "Soil health zone is Green"
    if zone == "Yellow":
        return 15, "Soil health zone is Yellow"
    if zone == "Red":
        return 5, "Soil health zone is Red"
    return 5, "No scored soil report on file — treated as highest risk"


def yield_consistency_points(count):
    if count >= 2:
        return 25, f"{count} yield predictions on record"
    if count == 1:
        return 15, "1 yield prediction on record"
    return 5, "No yield prediction history"


def farm_size_points(farm_size):
    if farm_size is None:
        return 5, "Farm size not on file — treated as smallest bracket"
    if farm_size > 10:
        return 20, f"Farm size {farm_size} acres is above 10 acres"
    if farm_size >= 5:
        return 15, f"Farm size {farm_size} acres is between 5 and 10 acres"
    if farm_size >= 2:
        return 10, f"Farm size {farm_size} acres is between 2 and 5 acres"
    return 5, f"Farm size {farm_size} acres is below 2 acres"


def crop_risk_points(crop_type):
    if crop_type is None:
        return 10, "No current crop on file — default medium risk assumed"
    if crop_type in LOW_RISK_CROPS:
        return 15, f"{crop_type.title()} is a low-risk staple crop"
    if crop_type in MEDIUM_RISK_CROPS:
        return 10, f"{crop_type.title()} is a medium-risk crop"
    if crop_type in HIGH_RISK_CROPS:
        return 7, f"{crop_type.title()} is a high-risk cash crop"
    return 10, f"{crop_type.title()} risk category not classified — default medium risk assumed"


def weather_risk_points(alert_count):
    if alert_count == 0:
        return 15, "No active weather alerts"
    if alert_count == 1:
        return 10, "1 active weather alert"
    return 5, f"{alert_count} active weather alerts"


@router.post("/register", response_model=BankRegisterResponse)
def register_bank_officer(payload: BankRegisterRequest):
    with get_db_cursor(commit=True) as cur:
        cur.execute("SELECT id FROM bank_officers WHERE phone = %s", (payload.phone,))
        existing = cur.fetchone()
        if existing:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "message": "Phone number already registered",
                },
            )

        hashed = hash_password(payload.password)

        cur.execute(
            """
            INSERT INTO bank_officers (name, phone, password, organization)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (payload.name, payload.phone, hashed, payload.organization),
        )
        officer_id = cur.fetchone()["id"]

    return BankRegisterResponse(
        success=True,
        message="Bank officer registered successfully",
        officer_id=officer_id,
    )


@router.post("/login", response_model=BankLoginResponse)
def login_bank_officer(payload: BankLoginRequest):
    with get_db_cursor() as cur:
        cur.execute(
            "SELECT id, name, password, organization FROM bank_officers WHERE phone = %s",
            (payload.phone,),
        )
        officer = cur.fetchone()

    if officer is None or not verify_password(payload.password, officer["password"]):
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "Invalid phone number or password",
            },
        )

    return BankLoginResponse(
        success=True,
        message="Login successful",
        officer_id=officer["id"],
        name=officer["name"],
        organization=officer["organization"],
    )


@router.get("/farmer/search", response_model=BankFarmerSearchResponse)
def search_farmer(phone: str):
    with get_db_cursor() as cur:
        cur.execute(
            "SELECT id, name, phone, village, district, state FROM farmers WHERE phone = %s",
            (phone,),
        )
        farmer = cur.fetchone()

    if farmer is None:
        raise HTTPException(status_code=404, detail="No farmer found with that phone number")

    return BankFarmerSearchResponse(
        success=True,
        farmer_id=farmer["id"],
        name=farmer["name"],
        phone=farmer["phone"],
        village=farmer["village"],
        district=farmer["district"],
        state=farmer["state"],
    )


@router.get("/farmer/{farmer_id}", response_model=BankFarmerProfileResponse)
def get_farmer_profile(farmer_id: int, bank_officer_id: Optional[int] = None):
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            "SELECT id, name, phone, village, taluka, district, state FROM farmers WHERE id = %s",
            (farmer_id,),
        )
        farmer = cur.fetchone()
        if farmer is None:
            raise HTTPException(status_code=404, detail="Farmer not found")

        if bank_officer_id is not None:
            cur.execute(
                "SELECT id FROM bank_officers WHERE id = %s",
                (bank_officer_id,),
            )
            if cur.fetchone() is None:
                raise HTTPException(status_code=404, detail="Bank officer not found")

            cur.execute(
                """
                INSERT INTO bank_farmer_views (farmer_id, bank_officer_id)
                VALUES (%s, %s)
                ON CONFLICT (farmer_id, bank_officer_id)
                DO UPDATE SET last_viewed_at = CURRENT_TIMESTAMP
                """,
                (farmer_id, bank_officer_id),
            )
            _portfolio_cache.pop(bank_officer_id, None)

        cur.execute(
            """
            SELECT farm_size, soil_type, water_source, crops_grown_before
            FROM farms WHERE farmer_id = %s
            ORDER BY id DESC LIMIT 1
            """,
            (farmer_id,),
        )
        farm = cur.fetchone()

        cur.execute(
            """
            SELECT id, nitrogen, phosphorus, potassium, ph, organic_carbon,
                   health_score, health_zone, report_date
            FROM soil_reports
            WHERE farmer_id = %s
            ORDER BY report_date DESC, id DESC
            LIMIT 1
            """,
            (farmer_id,),
        )
        latest_soil_report = cur.fetchone()

        cur.execute(
            """
            SELECT id, crop_type, crop_variety, sowing_date,
                   predicted_yield_min, predicted_yield_max, confidence_score, created_at
            FROM yield_predictions
            WHERE farmer_id = %s
            ORDER BY created_at DESC, id DESC
            """,
            (farmer_id,),
        )
        yield_predictions = cur.fetchall()

        cur.execute(
            """
            SELECT id, alert_type, alert_message, created_at
            FROM weather_alerts
            WHERE farmer_id = %s
            ORDER BY created_at DESC
            """,
            (farmer_id,),
        )
        weather_alerts = cur.fetchall()

    return BankFarmerProfileResponse(
        success=True,
        farmer_id=farmer["id"],
        name=farmer["name"],
        phone=farmer["phone"],
        village=farmer["village"],
        taluka=farmer["taluka"],
        district=farmer["district"],
        state=farmer["state"],
        farm_size=float(farm["farm_size"]) if farm and farm["farm_size"] is not None else None,
        soil_type=farm["soil_type"] if farm else None,
        water_source=farm["water_source"] if farm else None,
        crops_grown_before=farm["crops_grown_before"] if farm else None,
        latest_soil_report=latest_soil_report,
        latest_yield_prediction=yield_predictions[0] if yield_predictions else None,
        yield_prediction_history=yield_predictions,
        weather_alerts_history=weather_alerts,
    )


@router.post("/certificate/generate", response_model=CertificateGenerateResponse)
def generate_certificate(payload: CertificateGenerateRequest):
    with get_db_cursor(commit=True) as cur:
        cur.execute("SELECT id, name FROM bank_officers WHERE id = %s", (payload.bank_officer_id,))
        officer = cur.fetchone()
        if officer is None:
            raise HTTPException(status_code=404, detail="Bank officer not found")

        cur.execute(
            "SELECT id, name, village, taluka, district, state FROM farmers WHERE id = %s",
            (payload.farmer_id,),
        )
        farmer = cur.fetchone()
        if farmer is None:
            raise HTTPException(status_code=404, detail="Farmer not found")

        cur.execute(
            """
            SELECT farm_size, soil_type FROM farms
            WHERE farmer_id = %s ORDER BY id DESC LIMIT 1
            """,
            (payload.farmer_id,),
        )
        farm = cur.fetchone()

        cur.execute(
            """
            SELECT crop_type, crop_variety, predicted_yield_min, predicted_yield_max, confidence_score
            FROM yield_predictions WHERE farmer_id = %s
            ORDER BY created_at DESC, id DESC LIMIT 1
            """,
            (payload.farmer_id,),
        )
        yield_row = cur.fetchone()
        if yield_row is None:
            raise HTTPException(
                status_code=404,
                detail="No yield prediction found for this farmer. Predict yield first before generating a certificate.",
            )

        cur.execute(
            """
            SELECT health_score, health_zone FROM soil_reports
            WHERE farmer_id = %s ORDER BY report_date DESC, id DESC LIMIT 1
            """,
            (payload.farmer_id,),
        )
        soil_row = cur.fetchone()

        cur.execute(
            "SELECT COUNT(*) AS cnt FROM weather_alerts WHERE farmer_id = %s",
            (payload.farmer_id,),
        )
        alert_count = cur.fetchone()["cnt"]

        cur.execute(
            """
            INSERT INTO yield_certificates
                (farmer_id, bank_officer_id, crop_type, predicted_yield_min,
                 predicted_yield_max, confidence_score, soil_health_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, generated_at
            """,
            (
                payload.farmer_id,
                payload.bank_officer_id,
                yield_row["crop_type"],
                yield_row["predicted_yield_min"],
                yield_row["predicted_yield_max"],
                yield_row["confidence_score"],
                soil_row["health_score"] if soil_row else None,
            ),
        )
        cert_row = cur.fetchone()
        certificate_id = cert_row["id"]
        generated_at = cert_row["generated_at"]

        verification_code = uuid.uuid4().hex
        risk_text = weather_risk_text(alert_count)

        document_content = "|".join(
            str(v)
            for v in [
                certificate_id,
                payload.farmer_id,
                farmer["name"],
                yield_row["crop_type"],
                yield_row["predicted_yield_min"],
                yield_row["predicted_yield_max"],
                yield_row["confidence_score"],
                soil_row["health_score"] if soil_row else "NA",
                farm["farm_size"] if farm else "NA",
                farm["soil_type"] if farm else "NA",
                generated_at.isoformat(),
                verification_code,
            ]
        )
        document_hash = hashlib.sha256(document_content.encode("utf-8")).hexdigest()

        cur.execute(
            "UPDATE yield_certificates SET document_hash = %s, verification_code = %s WHERE id = %s",
            (document_hash, verification_code, certificate_id),
        )

    verify_url = f"{FRONTEND_BASE_URL}/bank/verify/{verification_code}"

    generate_yield_certificate_pdf(
        certificate_id=certificate_id,
        farmer_name=farmer["name"],
        village=farmer["village"],
        taluka=farmer["taluka"],
        district=farmer["district"],
        state=farmer["state"],
        farm_size=float(farm["farm_size"]) if farm and farm["farm_size"] is not None else None,
        soil_type=farm["soil_type"] if farm else None,
        crop_type=yield_row["crop_type"],
        crop_variety=yield_row["crop_variety"],
        predicted_yield_min=float(yield_row["predicted_yield_min"]),
        predicted_yield_max=float(yield_row["predicted_yield_max"]),
        confidence_score=float(yield_row["confidence_score"]),
        soil_health_score=soil_row["health_score"] if soil_row else None,
        soil_health_zone=soil_row["health_zone"] if soil_row else None,
        weather_risk_text=risk_text,
        document_hash=document_hash,
        verification_code=verification_code,
        verify_url=verify_url,
        generated_at=generated_at,
        bank_officer_name=officer["name"],
    )

    return CertificateGenerateResponse(
        success=True,
        certificate_id=certificate_id,
        verification_code=verification_code,
        document_hash=document_hash,
        pdf_download_url=f"/api/bank/certificate/{certificate_id}/pdf",
    )


@router.get("/certificate/verify/{verification_code}", response_model=CertificateVerifyResponse)
def verify_certificate(verification_code: str):
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT yc.id AS certificate_id, yc.crop_type, yc.predicted_yield_min,
                   yc.predicted_yield_max, yc.confidence_score, yc.soil_health_score,
                   yc.document_hash, yc.verification_code, yc.generated_at,
                   f.name AS farmer_name, f.village, f.district, f.state,
                   bo.name AS bank_officer_name
            FROM yield_certificates yc
            JOIN farmers f ON f.id = yc.farmer_id
            JOIN bank_officers bo ON bo.id = yc.bank_officer_id
            WHERE yc.verification_code = %s
            """,
            (verification_code,),
        )
        cert = cur.fetchone()

    if cert is None:
        raise HTTPException(status_code=404, detail="Certificate not found")

    return CertificateVerifyResponse(success=True, status="AUTHENTIC", **cert)


@router.get("/certificate/{certificate_id}/pdf")
def download_certificate_pdf(certificate_id: int):
    file_path = PDF_DIR / f"yield_certificate_{certificate_id}.pdf"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found for this certificate")

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=f"yield_certificate_{certificate_id}.pdf",
    )


@router.post("/loan/score", response_model=LoanScoreResponse)
def calculate_loan_score(payload: LoanScoreRequest):
    with get_db_cursor(commit=True) as cur:
        cur.execute("SELECT id FROM bank_officers WHERE id = %s", (payload.bank_officer_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Bank officer not found")

        cur.execute("SELECT id FROM farmers WHERE id = %s", (payload.farmer_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Farmer not found")

        cur.execute(
            """
            SELECT health_zone FROM soil_reports
            WHERE farmer_id = %s ORDER BY report_date DESC, id DESC LIMIT 1
            """,
            (payload.farmer_id,),
        )
        soil_row = cur.fetchone()

        cur.execute(
            "SELECT COUNT(*) AS cnt FROM yield_predictions WHERE farmer_id = %s",
            (payload.farmer_id,),
        )
        yield_count = cur.fetchone()["cnt"]

        cur.execute(
            """
            SELECT crop_type FROM yield_predictions
            WHERE farmer_id = %s ORDER BY created_at DESC, id DESC LIMIT 1
            """,
            (payload.farmer_id,),
        )
        latest_yield = cur.fetchone()

        cur.execute(
            "SELECT farm_size FROM farms WHERE farmer_id = %s ORDER BY id DESC LIMIT 1",
            (payload.farmer_id,),
        )
        farm_row = cur.fetchone()
        farm_size = (
            float(farm_row["farm_size"]) if farm_row and farm_row["farm_size"] is not None else None
        )

        cur.execute(
            "SELECT COUNT(*) AS cnt FROM weather_alerts WHERE farmer_id = %s",
            (payload.farmer_id,),
        )
        alert_count = cur.fetchone()["cnt"]

        soil_pts, soil_reason = soil_health_points(soil_row["health_zone"] if soil_row else None)
        yield_pts, yield_reason = yield_consistency_points(yield_count)
        size_pts, size_reason = farm_size_points(farm_size)
        crop_pts, crop_reason = crop_risk_points(latest_yield["crop_type"] if latest_yield else None)
        weather_pts, weather_reason = weather_risk_points(alert_count)

        total_score = soil_pts + yield_pts + size_pts + crop_pts + weather_pts

        if total_score >= 70:
            risk_level = "Low"
        elif total_score >= 40:
            risk_level = "Medium"
        else:
            risk_level = "High"

        base_per_acre = LOAN_BASE_PER_ACRE[risk_level]
        effective_farm_size = farm_size if farm_size else 1.0
        loan_min = round(base_per_acre * effective_farm_size * 0.8 / 1000) * 1000
        loan_max = round(base_per_acre * effective_farm_size * 1.2 / 1000) * 1000

        breakdown = [
            {"category": "Soil Health", "points_earned": soil_pts, "max_points": 25, "reason": soil_reason},
            {
                "category": "Yield Consistency",
                "points_earned": yield_pts,
                "max_points": 25,
                "reason": yield_reason,
            },
            {"category": "Farm Size", "points_earned": size_pts, "max_points": 20, "reason": size_reason},
            {"category": "Crop Risk", "points_earned": crop_pts, "max_points": 15, "reason": crop_reason},
            {
                "category": "Weather Risk",
                "points_earned": weather_pts,
                "max_points": 15,
                "reason": weather_reason,
            },
        ]

        cur.execute(
            """
            INSERT INTO loan_eligibility_scores
                (farmer_id, bank_officer_id, total_score, soil_health_points,
                 yield_consistency_points, farm_size_points, crop_risk_points,
                 weather_risk_points, score_breakdown)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                payload.farmer_id,
                payload.bank_officer_id,
                total_score,
                soil_pts,
                yield_pts,
                size_pts,
                crop_pts,
                weather_pts,
                psycopg2.extras.Json(breakdown),
            ),
        )

    return LoanScoreResponse(
        success=True,
        farmer_id=payload.farmer_id,
        total_score=total_score,
        risk_level=risk_level,
        breakdown=breakdown,
        recommended_loan_min=loan_min,
        recommended_loan_max=loan_max,
    )


@router.post("/claim/verify", response_model=ClaimVerifyResponse)
def verify_claim(payload: ClaimVerifyRequest):
    with get_db_cursor(commit=True) as cur:
        cur.execute("SELECT id FROM bank_officers WHERE id = %s", (payload.bank_officer_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Bank officer not found")

        cur.execute("SELECT id, district FROM farmers WHERE id = %s", (payload.farmer_id,))
        farmer = cur.fetchone()
        if farmer is None:
            raise HTTPException(status_code=404, detail="Farmer not found")
        if not farmer["district"]:
            raise HTTPException(
                status_code=400,
                detail="Farmer has no district on file; cannot determine location for weather data",
            )

        cur.execute(
            "SELECT latitude, longitude FROM districts WHERE LOWER(district_name) = LOWER(%s)",
            (farmer["district"],),
        )
        district_row = cur.fetchone()
        if district_row is None:
            raise HTTPException(
                status_code=404,
                detail=f"District '{farmer['district']}' not found in the districts lookup table",
            )

        cur.execute(
            """
            SELECT crop_type, crop_variety, sowing_date, predicted_yield_min,
                   predicted_yield_max, confidence_score
            FROM yield_predictions
            WHERE farmer_id = %s
            ORDER BY ABS(sowing_date - %s::date) ASC, id DESC
            LIMIT 1
            """,
            (payload.farmer_id, payload.claim_date),
        )
        yield_row = cur.fetchone()

        try:
            weather = fetch_historical_weather_for_date(
                float(district_row["latitude"]), float(district_row["longitude"]), payload.claim_date
            )
        except Exception as exc:
            weather = {
                "date": payload.claim_date.isoformat(),
                "rainfall_mm": None,
                "temp_max_c": None,
                "temp_min_c": None,
                "temp_mean_c": None,
                "warning": f"Live weather data unavailable ({exc.__class__.__name__}: {exc}).",
            }

        verification_result, explanation = evaluate_claim(payload.claimed_reason, weather)

        yield_data = None
        if yield_row:
            yield_data = {
                "crop_type": yield_row["crop_type"],
                "crop_variety": yield_row["crop_variety"],
                "sowing_date": yield_row["sowing_date"].isoformat(),
                "predicted_yield_min": float(yield_row["predicted_yield_min"]),
                "predicted_yield_max": float(yield_row["predicted_yield_max"]),
                "confidence_score": float(yield_row["confidence_score"]),
            }

        cur.execute(
            """
            INSERT INTO claim_verifications
                (farmer_id, bank_officer_id, claim_date, claimed_loss_amount, claimed_reason,
                 weather_data_on_claim_date, yield_prediction_at_time,
                 verification_result, verification_explanation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                payload.farmer_id,
                payload.bank_officer_id,
                payload.claim_date,
                payload.claimed_loss_amount,
                payload.claimed_reason,
                psycopg2.extras.Json(weather),
                psycopg2.extras.Json(yield_data),
                verification_result,
                explanation,
            ),
        )
        claim_verification_id = cur.fetchone()["id"]

    return ClaimVerifyResponse(
        success=True,
        claim_verification_id=claim_verification_id,
        verification_result=verification_result,
        explanation=explanation,
        weather_data=weather,
        yield_data=yield_data,
    )


@router.get("/portfolio/{officer_id}", response_model=PortfolioResponse)
def get_portfolio(officer_id: int):
    cached = _portfolio_cache.get(officer_id)
    if cached and (time.time() - cached[0]) < PORTFOLIO_CACHE_TTL_SECONDS:
        return cached[1]

    with get_db_cursor() as cur:
        cur.execute("SELECT id FROM bank_officers WHERE id = %s", (officer_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Bank officer not found")

        cur.execute(
            """
            WITH verified_farmers AS (
                SELECT farmer_id FROM yield_certificates WHERE bank_officer_id = %s
                UNION
                SELECT farmer_id FROM loan_eligibility_scores WHERE bank_officer_id = %s
                UNION
                SELECT farmer_id FROM claim_verifications WHERE bank_officer_id = %s
                UNION
                SELECT farmer_id FROM bank_farmer_views WHERE bank_officer_id = %s
            )
            SELECT
                f.id AS farmer_id, f.name, f.district,
                d.latitude, d.longitude,
                sr.health_score AS soil_health_score, sr.health_zone AS soil_health_zone,
                yp.crop_type, yp.predicted_yield_min, yp.predicted_yield_max,
                COALESCE(wa.alert_count, 0) AS active_weather_alerts
            FROM verified_farmers vf
            JOIN farmers f ON f.id = vf.farmer_id
            LEFT JOIN districts d ON LOWER(d.district_name) = LOWER(f.district)
            LEFT JOIN LATERAL (
                SELECT health_score, health_zone FROM soil_reports
                WHERE farmer_id = f.id ORDER BY report_date DESC, id DESC LIMIT 1
            ) sr ON true
            LEFT JOIN LATERAL (
                SELECT crop_type, predicted_yield_min, predicted_yield_max
                FROM yield_predictions
                WHERE farmer_id = f.id ORDER BY created_at DESC, id DESC LIMIT 1
            ) yp ON true
            LEFT JOIN LATERAL (
                SELECT COUNT(*) AS alert_count FROM weather_alerts WHERE farmer_id = f.id
            ) wa ON true
            ORDER BY f.name
            """,
            (officer_id, officer_id, officer_id, officer_id),
        )
        rows = cur.fetchall()

    farmers = []
    low_count = medium_count = high_count = 0

    for row in rows:
        has_yield = row["crop_type"] is not None
        risk_level = portfolio_risk_level(row["soil_health_zone"], row["active_weather_alerts"], has_yield)
        if risk_level == "LOW":
            low_count += 1
        elif risk_level == "MEDIUM":
            medium_count += 1
        else:
            high_count += 1

        farmers.append(
            {
                "farmer_id": row["farmer_id"],
                "name": row["name"],
                "district": row["district"],
                "latitude": float(row["latitude"]) if row["latitude"] is not None else None,
                "longitude": float(row["longitude"]) if row["longitude"] is not None else None,
                "crop_type": row["crop_type"],
                "soil_health_score": row["soil_health_score"],
                "soil_health_zone": row["soil_health_zone"],
                "active_weather_alerts": row["active_weather_alerts"],
                "predicted_yield_min": (
                    float(row["predicted_yield_min"]) if row["predicted_yield_min"] is not None else None
                ),
                "predicted_yield_max": (
                    float(row["predicted_yield_max"]) if row["predicted_yield_max"] is not None else None
                ),
                "risk_level": risk_level,
            }
        )

    response = PortfolioResponse(
        success=True,
        officer_id=officer_id,
        total_farmers=len(farmers),
        low_risk_count=low_count,
        medium_risk_count=medium_count,
        high_risk_count=high_count,
        farmers=farmers,
    )
    _portfolio_cache[officer_id] = (time.time(), response)
    return response


@router.get("/overview/{officer_id}", response_model=BankOverviewResponse)
def get_overview(officer_id: int):
    with get_db_cursor() as cur:
        cur.execute("SELECT id FROM bank_officers WHERE id = %s", (officer_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Bank officer not found")

        cur.execute(
            """
            SELECT COUNT(*) AS cnt FROM yield_certificates
            WHERE bank_officer_id = %s AND generated_at::date = CURRENT_DATE
            """,
            (officer_id,),
        )
        certificates_today = cur.fetchone()["cnt"]

        cur.execute(
            """
            SELECT COUNT(*) AS cnt FROM claim_verifications
            WHERE bank_officer_id = %s AND verification_result = 'INCONCLUSIVE'
            """,
            (officer_id,),
        )
        pending_claims = cur.fetchone()["cnt"]

    portfolio = get_portfolio(officer_id)

    return BankOverviewResponse(
        success=True,
        officer_id=officer_id,
        total_farmers_verified=portfolio.total_farmers,
        certificates_today=certificates_today,
        high_risk_farmers=portfolio.high_risk_count,
        pending_claim_verifications=pending_claims,
    )
