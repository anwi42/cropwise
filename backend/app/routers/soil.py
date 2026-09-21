from fastapi import APIRouter, File, HTTPException, UploadFile

from app.database import get_db_cursor
from app.ocr_utils import extract_soil_values, preprocess_image, run_ocr
from app.schemas import (
    SoilManualRequest,
    SoilManualResponse,
    SoilOCRResponse,
    SoilScoreRequest,
    SoilScoreResponse,
)
from app.soil_scoring import compute_soil_health

router = APIRouter(prefix="/api/soil", tags=["soil"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


@router.post("/ocr", response_model=SoilOCRResponse)
async def soil_ocr(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Upload a jpg, jpeg, png, or webp image.",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        preprocessed = preprocess_image(contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    ocr_results = run_ocr(preprocessed)
    extracted = extract_soil_values(ocr_results)
    needs_manual_review = any(
        field["needs_manual_correction"] for field in extracted.values()
    )

    return SoilOCRResponse(
        success=True,
        extracted_values=extracted,
        needs_manual_review=needs_manual_review,
    )


@router.post("/manual", response_model=SoilManualResponse)
def soil_manual(payload: SoilManualRequest):
    with get_db_cursor(commit=True) as cur:
        cur.execute("SELECT id FROM farmers WHERE id = %s", (payload.farmer_id,))
        farmer = cur.fetchone()
        if farmer is None:
            raise HTTPException(status_code=404, detail="Farmer not found")

        cur.execute(
            """
            INSERT INTO soil_reports
                (farmer_id, nitrogen, phosphorus, potassium, ph, organic_carbon,
                 report_date, input_method)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                payload.farmer_id,
                payload.nitrogen,
                payload.phosphorus,
                payload.potassium,
                payload.ph,
                payload.organic_carbon,
                payload.report_date,
                payload.input_method,
            ),
        )
        soil_report_id = cur.fetchone()["id"]

    return SoilManualResponse(
        success=True,
        message="Soil report saved successfully",
        soil_report_id=soil_report_id,
    )


@router.post("/score", response_model=SoilScoreResponse)
def soil_score(payload: SoilScoreRequest):
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            """
            SELECT id, farmer_id, nitrogen, phosphorus, potassium, ph, organic_carbon
            FROM soil_reports
            WHERE id = %s AND farmer_id = %s
            """,
            (payload.soil_report_id, payload.farmer_id),
        )
        soil_report = cur.fetchone()
        if soil_report is None:
            raise HTTPException(
                status_code=404,
                detail="Soil report not found for this farmer",
            )

        cur.execute(
            """
            SELECT nutrient, min_value, max_value, unit
            FROM icar_soil_standards
            WHERE crop_name = %s
            """,
            (payload.crop_planned,),
        )
        standard_rows = cur.fetchall()
        if not standard_rows:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No ICAR soil standards found for crop '{payload.crop_planned}'. "
                    "Supported crops: wheat, rice, tomato, onion, soybean, maize, "
                    "cotton, sugarcane."
                ),
            )

        standards = {
            row["nutrient"]: {
                "min_value": row["min_value"],
                "max_value": row["max_value"],
                "unit": row["unit"],
            }
            for row in standard_rows
        }

        soil_values = {
            "nitrogen": float(soil_report["nitrogen"]) if soil_report["nitrogen"] is not None else None,
            "phosphorus": float(soil_report["phosphorus"]) if soil_report["phosphorus"] is not None else None,
            "potassium": float(soil_report["potassium"]) if soil_report["potassium"] is not None else None,
            "ph": float(soil_report["ph"]) if soil_report["ph"] is not None else None,
            "organic_carbon": float(soil_report["organic_carbon"]) if soil_report["organic_carbon"] is not None else None,
        }

        health_score, health_zone, nutrient_details = compute_soil_health(
            soil_values, standards, payload.crop_planned
        )

        cur.execute(
            "UPDATE soil_reports SET health_score = %s, health_zone = %s WHERE id = %s",
            (health_score, health_zone, payload.soil_report_id),
        )

    return SoilScoreResponse(
        success=True,
        soil_report_id=payload.soil_report_id,
        crop_planned=payload.crop_planned,
        health_score=health_score,
        health_zone=health_zone,
        nutrient_details=nutrient_details,
    )
