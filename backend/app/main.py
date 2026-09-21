from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from app.routers import alerts, auth, crop, fertilizer, soil, yield_prediction
from app.weather_alerts import run_weather_alerts_job

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        run_weather_alerts_job,
        trigger=CronTrigger(hour=5, minute=0),
        id="daily_weather_alerts",
        replace_existing=True,
    )
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="Agri Platform API",
    description="AI-powered agricultural intelligence platform for Indian farmers",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(soil.router)
app.include_router(crop.router)
app.include_router(fertilizer.router)
app.include_router(yield_prediction.router)
app.include_router(alerts.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
