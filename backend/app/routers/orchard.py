import logging
from datetime import date

from fastapi import APIRouter, HTTPException

from app.database import get_db_cursor
from app.orchard_config import STAGE_ADVISORY, TREE_LABELS, get_orchard_stage
from app.schemas import OrchardAdvisoryRequest, OrchardAdvisoryResponse
from app.weather import fetch_daily_forecast_series, fetch_weather

router = APIRouter(prefix="/api/orchard", tags=["orchard"])

logger = logging.getLogger("orchard")

EXCESS_RAIN_TOTAL_MM = 100.0
EXCESS_RAIN_SINGLE_DAY_MM = 40.0
DROUGHT_TOTAL_RAIN_MM = 10.0
FROST_TEMP_C = 4.0
HIGH_HUMIDITY_PCT = 85.0


def _season_for_month(month: int) -> str:
    """Rough kharif/rabi/zaid bucket for a calendar month, used only to pick
    a sensible seasonal fallback if live weather data is unavailable."""
    if month in (6, 7, 8, 9, 10):
        return "kharif"
    if month in (4, 5):
        return "zaid"
    return "rabi"


def detect_weather_warnings(tree_type: str, stage: str, forecast: dict) -> list:
    warnings = []

    if stage == "flowering" and (
        forecast["total_rainfall_mm"] >= EXCESS_RAIN_TOTAL_MM
        or forecast["max_single_day_rainfall_mm"] >= EXCESS_RAIN_SINGLE_DAY_MM
    ):
        warnings.append(
            f"Heavy rain expected in the next 14 days ({forecast['total_rainfall_mm']} mm total) "
            f"while your {tree_type} trees are flowering. Excess rain now can cause flower and fruit "
            "drop; avoid extra irrigation and improve drainage around the base."
        )

    if stage == "fruit_development" and forecast["total_rainfall_mm"] <= DROUGHT_TOTAL_RAIN_MM:
        warnings.append(
            f"Very little rain expected in the next 14 days ({forecast['total_rainfall_mm']} mm total) "
            f"while your {tree_type} fruit is developing. Drought stress at this stage can reduce fruit "
            "size; arrange irrigation if water is available."
        )

    if stage == "harvest" and (
        forecast["total_rainfall_mm"] >= EXCESS_RAIN_TOTAL_MM
        or forecast["max_single_day_rainfall_mm"] >= EXCESS_RAIN_SINGLE_DAY_MM
    ):
        warnings.append(
            f"Heavy rain expected in the next 14 days during your {tree_type} harvest window. This can "
            "cause fruit cracking and spoilage; harvest ripe fruit promptly before the rain arrives."
        )

    if stage == "establishment" and forecast["min_temp_c"] <= FROST_TEMP_C:
        warnings.append(
            f"Night temperatures as low as {forecast['min_temp_c']} deg C are expected in the next 14 "
            f"days while your {tree_type} trees are still young. Frost can damage or kill young trees; "
            "consider covering them or light irrigation on the coldest nights."
        )

    if forecast["avg_humidity_pct"] is not None and forecast["avg_humidity_pct"] >= HIGH_HUMIDITY_PCT:
        warnings.append(
            f"Average humidity of {forecast['avg_humidity_pct']} percent is expected in the next 14 "
            f"days, which raises the risk of fungal disease on your {tree_type} trees. Watch for leaf "
            "spots or wilting and consider a preventive fungicide spray if humidity stays high."
        )

    return warnings


@router.post("/advisory", response_model=OrchardAdvisoryResponse)
def get_orchard_advisory(payload: OrchardAdvisoryRequest):
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
            "SELECT latitude, longitude FROM districts WHERE LOWER(district_name) = LOWER(%s)",
            (farmer["district"],),
        )
        district_row = cur.fetchone()
        if district_row is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"District '{farmer['district']}' not found in the districts lookup table, "
                    "so coordinates could not be resolved"
                ),
            )
        latitude = float(district_row["latitude"])
        longitude = float(district_row["longitude"])

        cur.execute(
            """
            INSERT INTO orchard_crops (farmer_id, tree_type, variety, planting_date, tree_count, area_acres)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                payload.farmer_id,
                payload.tree_type,
                payload.variety,
                payload.planting_date,
                payload.tree_count,
                payload.area_acres,
            ),
        )
        orchard_crop_id = cur.fetchone()["id"]

    today = date.today()
    years_since_planting = round((today - payload.planting_date).days / 365.25, 2)
    stage = get_orchard_stage(payload.tree_type, payload.planting_date, today)
    care = STAGE_ADVISORY[stage]

    weather = fetch_weather(latitude, longitude, _season_for_month(today.month))

    weather_warnings = []
    try:
        forecast = fetch_daily_forecast_series(latitude, longitude)
        weather_warnings = detect_weather_warnings(payload.tree_type, stage, forecast)
    except Exception as exc:
        logger.warning(
            "Could not compute weather warnings for orchard advisory (farmer %s): %s: %s",
            payload.farmer_id,
            exc.__class__.__name__,
            exc,
        )

    tree_label = TREE_LABELS.get(payload.tree_type, payload.tree_type.title())
    stage_label = stage.replace("_", " ")
    message = (
        f"Your {tree_label} trees are approximately {years_since_planting} years old and currently "
        f"in the {stage_label} stage."
    )

    return OrchardAdvisoryResponse(
        success=True,
        orchard_crop_id=orchard_crop_id,
        tree_type=payload.tree_type,
        variety=payload.variety,
        growth_stage=stage,
        years_since_planting=years_since_planting,
        weather=weather,
        care=care,
        weather_warnings=weather_warnings,
        message=message,
    )
