from datetime import date, datetime, timedelta, timezone

import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
REQUEST_TIMEOUT_SECONDS = 8
ARCHIVE_LAG_DAYS = 5
HISTORICAL_WINDOW_DAYS = 182

FALLBACK_WEATHER_BY_SEASON = {
    "kharif": {"rainfall_mm": 150.0, "avg_temperature_c": 28.0, "avg_humidity_pct": 75.0},
    "rabi": {"rainfall_mm": 20.0, "avg_temperature_c": 18.0, "avg_humidity_pct": 50.0},
    "zaid": {"rainfall_mm": 10.0, "avg_temperature_c": 30.0, "avg_humidity_pct": 30.0},
}


def fetch_weather(latitude: float, longitude: float, season: str) -> dict:
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        response = requests.get(
            OPEN_METEO_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
                "forecast_days": 14,
                "timezone": "auto",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        daily = data["daily"]

        precipitation = [v for v in daily["precipitation_sum"] if v is not None]
        daily_means = [
            (mx + mn) / 2
            for mx, mn in zip(daily["temperature_2m_max"], daily["temperature_2m_min"])
            if mx is not None and mn is not None
        ]

        if not daily_means:
            raise ValueError("Open-Meteo returned no usable temperature data")

        rainfall_total = sum(precipitation)
        avg_temperature = sum(daily_means) / len(daily_means)

        return {
            "rainfall_mm": round(rainfall_total, 2),
            "avg_temperature_c": round(avg_temperature, 2),
            "source": "open-meteo",
            "fallback_used": False,
            "warning": None,
            "timestamp": timestamp,
        }

    except Exception as exc:
        fallback = FALLBACK_WEATHER_BY_SEASON.get(
            season, FALLBACK_WEATHER_BY_SEASON["kharif"]
        )
        return {
            "rainfall_mm": fallback["rainfall_mm"],
            "avg_temperature_c": fallback["avg_temperature_c"],
            "source": "seasonal_fallback",
            "fallback_used": True,
            "warning": (
                f"Live weather data unavailable ({exc.__class__.__name__}). "
                "Used a seasonal average as fallback so the request could still complete."
            ),
            "timestamp": timestamp,
        }


def _daily_stats(daily: dict) -> dict:
    precipitation = [v for v in daily["precipitation_sum"] if v is not None]
    temps = [v for v in daily["temperature_2m_mean"] if v is not None]
    humidity = [v for v in daily["relative_humidity_2m_mean"] if v is not None]

    if not temps or not humidity:
        raise ValueError("Open-Meteo returned no usable temperature/humidity data")

    return {
        "rainfall_mm": sum(precipitation),
        "avg_temperature_c": sum(temps) / len(temps),
        "avg_humidity_pct": sum(humidity) / len(humidity),
        "day_count": len(temps),
    }


def fetch_historical_weather(latitude: float, longitude: float) -> dict:
    end_date = date.today() - timedelta(days=ARCHIVE_LAG_DAYS)
    start_date = end_date - timedelta(days=HISTORICAL_WINDOW_DAYS)

    response = requests.get(
        OPEN_METEO_ARCHIVE_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": "precipitation_sum,temperature_2m_mean,relative_humidity_2m_mean",
            "timezone": "auto",
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return _daily_stats(response.json()["daily"])


def fetch_forecast_weather_with_humidity(latitude: float, longitude: float, days: int = 14) -> dict:
    response = requests.get(
        OPEN_METEO_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "daily": "precipitation_sum,temperature_2m_mean,relative_humidity_2m_mean",
            "forecast_days": days,
            "timezone": "auto",
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return _daily_stats(response.json()["daily"])


def fetch_daily_forecast_series(latitude: float, longitude: float, days: int = 14) -> dict:
    response = requests.get(
        OPEN_METEO_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "daily": "precipitation_sum,temperature_2m_min,temperature_2m_max,relative_humidity_2m_mean",
            "forecast_days": days,
            "timezone": "auto",
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    daily = response.json()["daily"]

    days_data = []
    for i, day in enumerate(daily["time"]):
        temp_min = daily["temperature_2m_min"][i]
        temp_max = daily["temperature_2m_max"][i]
        if temp_min is None or temp_max is None:
            continue
        precipitation = daily["precipitation_sum"][i]
        humidity = daily["relative_humidity_2m_mean"][i]
        days_data.append(
            {
                "date": day,
                "rainfall_mm": precipitation if precipitation is not None else 0.0,
                "temp_min_c": temp_min,
                "temp_max_c": temp_max,
                "humidity_pct": humidity,
            }
        )

    if not days_data:
        raise ValueError("Open-Meteo returned no usable forecast data")

    humidity_values = [d["humidity_pct"] for d in days_data if d["humidity_pct"] is not None]

    return {
        "days": days_data,
        "total_rainfall_mm": round(sum(d["rainfall_mm"] for d in days_data), 2),
        "max_single_day_rainfall_mm": round(max(d["rainfall_mm"] for d in days_data), 2),
        "min_temp_c": round(min(d["temp_min_c"] for d in days_data), 2),
        "avg_humidity_pct": (
            round(sum(humidity_values) / len(humidity_values), 2) if humidity_values else None
        ),
    }


def fetch_yield_weather(latitude: float, longitude: float, season: str) -> dict:
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        historical = fetch_historical_weather(latitude, longitude)
        forecast = fetch_forecast_weather_with_humidity(latitude, longitude)

        total_days = historical["day_count"] + forecast["day_count"]
        rainfall_total = historical["rainfall_mm"] + forecast["rainfall_mm"]
        avg_temperature = (
            historical["avg_temperature_c"] * historical["day_count"]
            + forecast["avg_temperature_c"] * forecast["day_count"]
        ) / total_days
        avg_humidity = (
            historical["avg_humidity_pct"] * historical["day_count"]
            + forecast["avg_humidity_pct"] * forecast["day_count"]
        ) / total_days

        return {
            "rainfall_mm": round(rainfall_total, 2),
            "avg_temperature_c": round(avg_temperature, 2),
            "avg_humidity_pct": round(avg_humidity, 2),
            "source": "open-meteo",
            "fallback_used": False,
            "warning": None,
            "timestamp": timestamp,
        }

    except Exception as exc:
        fallback = FALLBACK_WEATHER_BY_SEASON.get(
            season, FALLBACK_WEATHER_BY_SEASON["kharif"]
        )
        return {
            "rainfall_mm": fallback["rainfall_mm"],
            "avg_temperature_c": fallback["avg_temperature_c"],
            "avg_humidity_pct": fallback["avg_humidity_pct"],
            "source": "seasonal_fallback",
            "fallback_used": True,
            "warning": (
                f"Live weather data unavailable ({exc.__class__.__name__}). "
                "Used a seasonal average as fallback so the request could still complete."
            ),
            "timestamp": timestamp,
        }
