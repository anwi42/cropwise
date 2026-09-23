import logging
from datetime import date

from app.crop_stage_config import TOTAL_CROP_DURATION_DAYS, get_current_growth_stage
from app.database import get_db_cursor
from app.weather import fetch_daily_forecast_series

logger = logging.getLogger("weather_alerts")

EXCESS_RAIN_TOTAL_MM = 100.0
EXCESS_RAIN_SINGLE_DAY_MM = 40.0
DROUGHT_TOTAL_RAIN_MM = 10.0
FROST_TEMP_C = 4.0
HIGH_HUMIDITY_PCT = 85.0


def detect_dangerous_patterns(crop: str, stage: str, forecast: dict) -> list:
    """Compare a 14-day forecast against a farmer's current crop stage.

    Returns a list of {"alert_type", "alert_message"} dicts, one per
    dangerous pattern found. Can return more than one for the same farmer
    (e.g. drought stress and fungal risk can both apply at once).
    """
    alerts = []

    if stage == "flowering" and (
        forecast["total_rainfall_mm"] >= EXCESS_RAIN_TOTAL_MM
        or forecast["max_single_day_rainfall_mm"] >= EXCESS_RAIN_SINGLE_DAY_MM
    ):
        alerts.append(
            {
                "alert_type": "excess_rain_flowering",
                "alert_message": (
                    f"Heavy rain expected in the next 14 days ({forecast['total_rainfall_mm']} mm "
                    f"total, up to {forecast['max_single_day_rainfall_mm']} mm in a single day) while "
                    f"your {crop} crop is flowering. Excess rain now can cause flower drop and reduce "
                    "pollination. Consider improving field drainage and delaying any planned irrigation."
                ),
            }
        )

    if stage == "grain_filling" and forecast["total_rainfall_mm"] <= DROUGHT_TOTAL_RAIN_MM:
        alerts.append(
            {
                "alert_type": "drought_grain_filling",
                "alert_message": (
                    f"Very little rain expected in the next 14 days ({forecast['total_rainfall_mm']} mm "
                    f"total) while your {crop} crop is filling grain/fruit. Drought stress at this stage "
                    "can reduce grain weight and final yield. Arrange irrigation if water is available."
                ),
            }
        )

    if stage == "seedling" and forecast["min_temp_c"] <= FROST_TEMP_C:
        alerts.append(
            {
                "alert_type": "frost_risk_seedling",
                "alert_message": (
                    f"Night temperatures as low as {forecast['min_temp_c']} deg C are expected in the "
                    f"next 14 days while your {crop} seedlings are still young. Frost can kill young "
                    "seedlings. Consider light evening irrigation or covering nursery beds on the "
                    "coldest nights."
                ),
            }
        )

    if forecast["avg_humidity_pct"] is not None and forecast["avg_humidity_pct"] >= HIGH_HUMIDITY_PCT:
        alerts.append(
            {
                "alert_type": "high_humidity_fungal_risk",
                "alert_message": (
                    f"Average humidity of {forecast['avg_humidity_pct']} percent is expected in the "
                    f"next 14 days, which raises the risk of fungal disease on your {crop} crop. Watch "
                    "for leaf spots or wilting and consider a preventive fungicide spray if humidity "
                    "stays high."
                ),
            }
        )

    return alerts


def _load_farmers_with_active_crop(cur) -> list:
    cur.execute(
        """
        SELECT f.id AS farmer_id, f.district, d.latitude, d.longitude,
               yp.crop_type, yp.sowing_date
        FROM farmers f
        JOIN districts d ON LOWER(d.district_name) = LOWER(f.district)
        LEFT JOIN LATERAL (
            SELECT crop_type, sowing_date
            FROM yield_predictions
            WHERE farmer_id = f.id
            ORDER BY sowing_date DESC, id DESC
            LIMIT 1
        ) yp ON true
        WHERE f.district IS NOT NULL
        """
    )
    return cur.fetchall()


def _alert_already_created_today(cur, farmer_id: int, alert_type: str) -> bool:
    cur.execute(
        """
        SELECT 1 FROM weather_alerts
        WHERE farmer_id = %s AND alert_type = %s AND created_at::date = CURRENT_DATE
        LIMIT 1
        """,
        (farmer_id, alert_type),
    )
    return cur.fetchone() is not None


def run_weather_alerts_job() -> dict:
    """Daily job: scan every farmer's current crop stage against the 14-day
    forecast for their district and raise weather_alerts rows for any
    dangerous pattern. Scheduled for 5am IST in main.py; safe to call
    manually (e.g. via POST /api/alerts/run-check) for testing.

    Never raises — a failure for one farmer (bad district, Open-Meteo
    outage) is logged and skipped so the rest of the run still completes.
    """
    today = date.today()
    farmers_checked = 0
    farmers_skipped_no_crop = 0
    alerts_created = 0

    with get_db_cursor() as cur:
        farmers = _load_farmers_with_active_crop(cur)

    for farmer in farmers:
        farmers_checked += 1
        crop = farmer["crop_type"]
        sowing_date = farmer["sowing_date"]

        if crop is None or sowing_date is None:
            farmers_skipped_no_crop += 1
            continue

        total_duration = TOTAL_CROP_DURATION_DAYS.get(crop)
        if total_duration is None:
            continue

        days_after_sowing = (today - sowing_date).days
        if days_after_sowing < 0 or days_after_sowing > total_duration:
            continue

        stage = get_current_growth_stage(crop, days_after_sowing)
        if stage is None:
            continue

        try:
            forecast = fetch_daily_forecast_series(
                float(farmer["latitude"]), float(farmer["longitude"])
            )
        except Exception as exc:
            logger.warning(
                "Skipping weather alert check for farmer %s: forecast fetch failed (%s: %s)",
                farmer["farmer_id"],
                exc.__class__.__name__,
                exc,
            )
            continue

        triggered = detect_dangerous_patterns(crop, stage, forecast)
        if not triggered:
            continue

        with get_db_cursor(commit=True) as cur:
            for alert in triggered:
                if _alert_already_created_today(cur, farmer["farmer_id"], alert["alert_type"]):
                    continue
                cur.execute(
                    """
                    INSERT INTO weather_alerts (farmer_id, alert_message, alert_type)
                    VALUES (%s, %s, %s)
                    """,
                    (farmer["farmer_id"], alert["alert_message"], alert["alert_type"]),
                )
                alerts_created += 1

    logger.info(
        "Weather alerts job finished: %s farmers checked, %s skipped (no active crop), %s alerts created",
        farmers_checked,
        farmers_skipped_no_crop,
        alerts_created,
    )
    return {
        "farmers_checked": farmers_checked,
        "farmers_skipped_no_crop": farmers_skipped_no_crop,
        "alerts_created": alerts_created,
    }
