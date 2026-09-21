from fastapi import APIRouter, HTTPException

from app.database import get_db_cursor
from app.schemas import AlertsCheckResponse, AlertsResponse
from app.weather_alerts import run_weather_alerts_job

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("/run-check", response_model=AlertsCheckResponse)
def run_check():
    """Manually trigger the same scan the 5am scheduled job runs.

    Not part of the farmer-facing spec, but the job otherwise only runs
    once a day, so this is how the feature gets tested/verified.
    """
    result = run_weather_alerts_job()
    return AlertsCheckResponse(success=True, **result)


@router.get("/{farmer_id}", response_model=AlertsResponse)
def get_alerts(farmer_id: int):
    with get_db_cursor(commit=True) as cur:
        cur.execute("SELECT id FROM farmers WHERE id = %s", (farmer_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Farmer not found")

        cur.execute(
            """
            SELECT id, alert_message, alert_type, created_at
            FROM weather_alerts
            WHERE farmer_id = %s AND is_read = FALSE
            ORDER BY created_at DESC
            """,
            (farmer_id,),
        )
        unread_alerts = cur.fetchall()

        if unread_alerts:
            cur.execute(
                "UPDATE weather_alerts SET is_read = TRUE WHERE id = ANY(%s)",
                ([row["id"] for row in unread_alerts],),
            )

    return AlertsResponse(
        success=True,
        farmer_id=farmer_id,
        alerts=[
            {
                "id": row["id"],
                "alert_type": row["alert_type"],
                "alert_message": row["alert_message"],
                "created_at": row["created_at"],
            }
            for row in unread_alerts
        ],
    )
