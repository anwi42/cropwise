from fastapi import APIRouter, HTTPException

from app.crop_config import CROP_WEATHER_RANGES, SEASON_ENCODING
from app.database import get_db_cursor
from app.schemas import YieldPredictRequest, YieldPredictResponse
from app.soil_scoring import compute_soil_health, score_nutrient
from app.weather import fetch_yield_weather
from app.yield_config import (
    CROP_ENCODING,
    FEATURE_ORDER,
    HUMIDITY_RANGE_BY_SEASON,
    SOIL_TYPE_ENCODING,
    derive_season_from_sowing_date,
)
from app.yield_model import predict_yield

router = APIRouter(prefix="/api/yield", tags=["yield"])

DEFAULT_FARM_SIZE_ACRES = 1.0


@router.post("/predict", response_model=YieldPredictResponse)
def predict(payload: YieldPredictRequest):
    with get_db_cursor(commit=True) as cur:
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
            """
            SELECT nitrogen, phosphorus, potassium, ph, organic_carbon
            FROM soil_reports
            WHERE farmer_id = %s
            ORDER BY report_date DESC, id DESC
            LIMIT 1
            """,
            (payload.farmer_id,),
        )
        soil_report = cur.fetchone()
        if soil_report is None:
            raise HTTPException(
                status_code=404,
                detail="No soil report found for this farmer. Submit a soil report first.",
            )

        cur.execute(
            """
            SELECT soil_type, farm_size FROM farms
            WHERE farmer_id = %s AND soil_type IS NOT NULL AND soil_type <> ''
            ORDER BY id DESC LIMIT 1
            """,
            (payload.farmer_id,),
        )
        farm = cur.fetchone()
        if farm is None:
            raise HTTPException(
                status_code=400,
                detail="This farmer has no soil_type on file; cannot predict yield",
            )
        soil_type = farm["soil_type"]
        farm_size = float(farm["farm_size"]) if farm["farm_size"] is not None else DEFAULT_FARM_SIZE_ACRES

        cur.execute(
            "SELECT latitude, longitude FROM districts WHERE district_name = %s",
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

        cur.execute(
            """
            SELECT nutrient, min_value, max_value, unit
            FROM icar_soil_standards
            WHERE crop_name = %s
            """,
            (payload.crop_type,),
        )
        standard_rows = cur.fetchall()
        if not standard_rows:
            raise HTTPException(
                status_code=404,
                detail=f"No ICAR soil standards found for crop '{payload.crop_type}'",
            )
        standards = {
            row["nutrient"]: {
                "min_value": row["min_value"],
                "max_value": row["max_value"],
                "unit": row["unit"],
            }
            for row in standard_rows
        }
        standards_minmax = {
            nutrient: (float(v["min_value"]), float(v["max_value"]))
            for nutrient, v in standards.items()
        }

        season = derive_season_from_sowing_date(payload.sowing_date)

        weather = fetch_yield_weather(
            float(district_row["latitude"]), float(district_row["longitude"]), season
        )

        soil_values = {
            "nitrogen": float(soil_report["nitrogen"]),
            "phosphorus": float(soil_report["phosphorus"]),
            "potassium": float(soil_report["potassium"]),
            "ph": float(soil_report["ph"]),
            "organic_carbon": float(soil_report["organic_carbon"]),
        }

        soil_fit_score, _, _ = compute_soil_health(soil_values, standards, payload.crop_type)

        rain_min, rain_max, temp_min, temp_max = CROP_WEATHER_RANGES[payload.crop_type]
        humidity_min, humidity_max = HUMIDITY_RANGE_BY_SEASON[season]

        weather_scores = [
            score_nutrient(weather["rainfall_mm"], rain_min, rain_max)[1],
            score_nutrient(weather["avg_temperature_c"], temp_min, temp_max)[1],
        ]
        weather_fit_score = sum(weather_scores) / len(weather_scores)
        humidity_fit_score = score_nutrient(
            weather["avg_humidity_pct"], humidity_min, humidity_max
        )[1]

        confidence_score = round(
            0.55 * soil_fit_score + 0.35 * weather_fit_score + 0.10 * humidity_fit_score,
            2,
        )

        feature_values_by_name = {
            "nitrogen": soil_values["nitrogen"],
            "phosphorus": soil_values["phosphorus"],
            "potassium": soil_values["potassium"],
            "ph": soil_values["ph"],
            "organic_carbon": soil_values["organic_carbon"],
            "soil_type": SOIL_TYPE_ENCODING.get(soil_type, SOIL_TYPE_ENCODING["loamy"]),
            "farm_size": farm_size,
            "rainfall": weather["rainfall_mm"],
            "avg_temperature": weather["avg_temperature_c"],
            "avg_humidity": weather["avg_humidity_pct"],
            "crop": CROP_ENCODING[payload.crop_type],
            "sowing_day_of_year": payload.sowing_date.timetuple().tm_yday,
            "season": SEASON_ENCODING[season],
        }
        feature_values = [feature_values_by_name[name] for name in FEATURE_ORDER]

        prediction = predict_yield(feature_values)

        message = (
            f"Predicted yield for {payload.crop_type} ({payload.crop_variety}) sown on "
            f"{payload.sowing_date.isoformat()}, based on your soil report and {season} "
            "season weather."
        )

        cur.execute(
            """
            INSERT INTO yield_predictions
                (farmer_id, crop_type, crop_variety, sowing_date,
                 predicted_yield_min, predicted_yield_max, confidence_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                payload.farmer_id,
                payload.crop_type,
                payload.crop_variety,
                payload.sowing_date,
                round(prediction["low"], 2),
                round(prediction["high"], 2),
                confidence_score,
            ),
        )
        yield_prediction_id = cur.fetchone()["id"]

    return YieldPredictResponse(
        success=True,
        yield_prediction_id=yield_prediction_id,
        crop_type=payload.crop_type,
        crop_variety=payload.crop_variety,
        season=season,
        weather=weather,
        soil_fit_score=soil_fit_score,
        predicted_yield_min=round(prediction["low"], 2),
        predicted_yield_max=round(prediction["high"], 2),
        confidence_score=confidence_score,
        message=message,
    )
