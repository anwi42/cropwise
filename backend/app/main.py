from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import alerts, auth, bank, crop, fertilizer, orchard, soil, yield_prediction
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(bank.router)
app.include_router(soil.router)
app.include_router(crop.router)
app.include_router(fertilizer.router)
app.include_router(yield_prediction.router)
app.include_router(alerts.router)
app.include_router(orchard.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
