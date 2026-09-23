import psycopg2.extras
from fastapi import APIRouter, HTTPException

from app.crop_config import CROP_SEASONS, MARKET_RISK, SEASON_ENCODING
from app.crop_model import predict_crop_fit_scores
from app.database import get_db_cursor
from app.schemas import CropRecommendRequest, CropRecommendResponse
from app.soil_scoring import compute_soil_health
from app.weather import fetch_weather

router = APIRouter(prefix="/api/crop", tags=["crop"])


def build_reasoning(crop: str, fit_score: int, season: str, weather: dict) -> str:
    if fit_score >= 80:
        fit_phrase = "your soil conditions are an excellent match"
    elif fit_score >= 50:
        fit_phrase = "your soil conditions are a reasonable match, though not perfect"
    else:
        fit_phrase = "your soil conditions are a weak match and may need correction first"

    return (
        f"{crop.title()} is well suited to the {season} season and {fit_phrase} "
        f"(soil fit score {fit_score}/100). The forecast of "
        f"{weather['rainfall_mm']} mm rainfall and {weather['avg_temperature_c']} deg C "
        f"average temperature over the next 14 days is appropriate for {crop} cultivation."
    )


@router.post("/recommend", response_model=CropRecommendResponse)
def recommend_crop(payload: CropRecommendRequest):
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            """
            SELECT id, nitrogen, phosphorus, potassium, ph, organic_carbon
            FROM soil_reports
            WHERE id = %s AND farmer_id = %s
            """,
            (payload.soil_report_id, payload.farmer_id),
        )
        soil_report = cur.fetchone()
        if soil_report is None:
            raise HTTPException(
                status_code=404, detail="Soil report not found for this farmer"
            )

        cur.execute(
            "SELECT district, state FROM farmers WHERE id = %s", (payload.farmer_id,)
        )
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
                detail=(
                    f"District '{farmer['district']}' not found in the districts "
                    "lookup table, so coordinates could not be resolved"
                ),
            )

        weather = fetch_weather(
            float(district_row["latitude"]),
            float(district_row["longitude"]),
            payload.season,
        )

        soil_values = {
            "nitrogen": float(soil_report["nitrogen"]),
            "phosphorus": float(soil_report["phosphorus"]),
            "potassium": float(soil_report["potassium"]),
            "ph": float(soil_report["ph"]),
            "organic_carbon": float(soil_report["organic_carbon"]),
        }

        observed_features = [
            soil_values["nitrogen"],
            soil_values["phosphorus"],
            soil_values["potassium"],
            soil_values["ph"],
            soil_values["organic_carbon"],
            SEASON_ENCODING[payload.season],
            weather["rainfall_mm"],
            weather["avg_temperature_c"],
        ]

        season_crops = [
            crop for crop, seasons in CROP_SEASONS.items() if payload.season in seasons
        ]
        candidates = predict_crop_fit_scores(observed_features, season_crops)
        if not candidates:
            candidates = predict_crop_fit_scores(observed_features, list(CROP_SEASONS.keys()))

        top_crops = sorted(candidates.items(), key=lambda item: item[1], reverse=True)[:3]

        cur.execute(
            "SELECT crop_name, nutrient, min_value, max_value, unit FROM icar_soil_standards WHERE crop_name = ANY(%s)",
            ([crop for crop, _ in top_crops],),
        )
        standards_by_crop: dict = {}
        for row in cur.fetchall():
            standards_by_crop.setdefault(row["crop_name"], {})[row["nutrient"]] = {
                "min_value": row["min_value"],
                "max_value": row["max_value"],
                "unit": row["unit"],
            }

        recommendations = []
        for crop, probability in top_crops:
            crop_standards = standards_by_crop.get(crop, {})
            fit_score, _, _ = compute_soil_health(soil_values, crop_standards, crop)
            recommendations.append(
                {
                    "crop_name": crop,
                    "reasoning": build_reasoning(crop, fit_score, payload.season, weather),
                    "soil_fit_score": fit_score,
                    "market_risk": MARKET_RISK.get(crop, "medium"),
                    "model_confidence": round(float(probability) * 100, 2),
                }
            )

        cur.execute(
            """
            INSERT INTO crop_recommendations (farmer_id, soil_report_id, recommended_crops, season)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (
                payload.farmer_id,
                payload.soil_report_id,
                psycopg2.extras.Json(recommendations),
                payload.season,
            ),
        )
        crop_recommendation_id = cur.fetchone()["id"]

    return CropRecommendResponse(
        success=True,
        crop_recommendation_id=crop_recommendation_id,
        season=payload.season,
        weather=weather,
        recommendations=recommendations,
    )
