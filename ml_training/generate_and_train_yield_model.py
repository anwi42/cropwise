import random
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

from app.crop_config import CROP_SEASONS, CROP_WEATHER_RANGES, SEASON_ENCODING
from app.database import get_db_cursor
from app.soil_scoring import score_nutrient
from app.yield_config import (
    BASE_YIELD_RANGE_TONS_PER_ACRE,
    CROP_ENCODING,
    FEATURE_ORDER,
    HUMIDITY_RANGE_BY_SEASON,
    SOIL_TYPE_ENCODING,
    SOWING_DAY_OF_YEAR_RANGE_BY_SEASON,
)

SAMPLES_PER_CROP_SEASON = 250
RANDOM_SEED = 42

MODELS_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODELS_DIR / "yield_models.joblib"


def fetch_soil_standards() -> dict:
    with get_db_cursor() as cur:
        cur.execute(
            "SELECT crop_name, nutrient, min_value, max_value FROM icar_soil_standards"
        )
        rows = cur.fetchall()

    standards: dict = {}
    for row in rows:
        crop = row["crop_name"]
        standards.setdefault(crop, {})[row["nutrient"]] = (
            float(row["min_value"]),
            float(row["max_value"]),
        )
    return standards


def sample_with_margin(min_v: float, max_v: float, rng: np.random.Generator, margin: float = 0.2) -> float:
    span = max_v - min_v
    low = min_v - span * margin
    high = max_v + span * margin
    return float(rng.uniform(max(low, 0.0), high))


def fit_fraction(value: float, min_v: float, max_v: float) -> float:
    _, score = score_nutrient(value, min_v, max_v)
    return score / 100.0


def generate_training_rows(standards: dict, rng: np.random.Generator) -> pd.DataFrame:
    records = []
    soil_types = list(SOIL_TYPE_ENCODING.keys())

    for crop, seasons in CROP_SEASONS.items():
        crop_standards = standards.get(crop)
        base_low, base_high = BASE_YIELD_RANGE_TONS_PER_ACRE[crop]
        rain_min, rain_max, temp_min, temp_max = CROP_WEATHER_RANGES[crop]

        n_min, n_max = crop_standards["nitrogen"]
        p_min, p_max = crop_standards["phosphorus"]
        k_min, k_max = crop_standards["potassium"]
        ph_min, ph_max = crop_standards["ph"]
        oc_min, oc_max = crop_standards["organic_carbon"]

        for season in seasons:
            humidity_min, humidity_max = HUMIDITY_RANGE_BY_SEASON[season]
            doy_min, doy_max = SOWING_DAY_OF_YEAR_RANGE_BY_SEASON[season]

            for _ in range(SAMPLES_PER_CROP_SEASON):
                nitrogen = sample_with_margin(n_min, n_max, rng)
                phosphorus = sample_with_margin(p_min, p_max, rng)
                potassium = sample_with_margin(k_min, k_max, rng)
                ph = min(14.0, max(0.0, sample_with_margin(ph_min, ph_max, rng)))
                organic_carbon = max(0.0, sample_with_margin(oc_min, oc_max, rng))
                rainfall = max(0.0, sample_with_margin(rain_min, rain_max, rng))
                temperature = sample_with_margin(temp_min, temp_max, rng)
                humidity = max(0.0, min(100.0, sample_with_margin(humidity_min, humidity_max, rng)))
                farm_size = float(rng.uniform(0.5, 10.0))
                soil_type = random.choice(soil_types)
                sowing_doy = int(rng.uniform(doy_min, doy_max))

                soil_fit = np.mean(
                    [
                        fit_fraction(nitrogen, n_min, n_max),
                        fit_fraction(phosphorus, p_min, p_max),
                        fit_fraction(potassium, k_min, k_max),
                        fit_fraction(ph, ph_min, ph_max),
                        fit_fraction(organic_carbon, oc_min, oc_max),
                    ]
                )
                weather_fit = np.mean(
                    [
                        fit_fraction(rainfall, rain_min, rain_max),
                        fit_fraction(temperature, temp_min, temp_max),
                    ]
                )
                humidity_fit = fit_fraction(humidity, humidity_min, humidity_max)

                noise_factor = float(rng.uniform(0.85, 1.0))
                suitability = np.clip(
                    0.5 * soil_fit + 0.3 * weather_fit + 0.1 * humidity_fit + 0.1 * noise_factor,
                    0.0,
                    1.0,
                )

                target_yield = base_low + (base_high - base_low) * suitability
                target_yield += float(rng.normal(0, (base_high - base_low) * 0.04))
                target_yield = max(base_low * 0.5, min(base_high * 1.1, target_yield))

                records.append(
                    {
                        "nitrogen": nitrogen,
                        "phosphorus": phosphorus,
                        "potassium": potassium,
                        "ph": ph,
                        "organic_carbon": organic_carbon,
                        "soil_type": SOIL_TYPE_ENCODING[soil_type],
                        "farm_size": farm_size,
                        "rainfall": rainfall,
                        "avg_temperature": temperature,
                        "avg_humidity": humidity,
                        "crop": CROP_ENCODING[crop],
                        "sowing_day_of_year": sowing_doy,
                        "season": SEASON_ENCODING[season],
                        "yield_tons_per_acre": target_yield,
                    }
                )

    return pd.DataFrame.from_records(records)


def train_models(df: pd.DataFrame) -> dict:
    X = df[FEATURE_ORDER]
    y = df["yield_tons_per_acre"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED
    )

    common_params = dict(
        n_estimators=250,
        max_depth=5,
        learning_rate=0.08,
        random_state=RANDOM_SEED,
        verbosity=0,
    )

    median_model = xgb.XGBRegressor(objective="reg:squarederror", **common_params)
    median_model.fit(X_train, y_train)

    low_model = xgb.XGBRegressor(
        objective="reg:quantileerror", quantile_alpha=0.1, **common_params
    )
    low_model.fit(X_train, y_train)

    high_model = xgb.XGBRegressor(
        objective="reg:quantileerror", quantile_alpha=0.9, **common_params
    )
    high_model.fit(X_train, y_train)

    mae = mean_absolute_error(y_test, median_model.predict(X_test))
    print(f"Median model test MAE: {mae:.4f} tons/acre on {len(X_test)} held-out samples")

    return {"low": low_model, "median": median_model, "high": high_model}


def main():
    rng = np.random.default_rng(RANDOM_SEED)
    random.seed(RANDOM_SEED)

    print("Fetching ICAR soil standards from database...")
    standards = fetch_soil_standards()

    print("Generating synthetic yield training data grounded in ICAR ranges + crop weather profiles...")
    df = generate_training_rows(standards, rng)
    print(f"Generated {len(df)} training rows across {df['crop'].nunique()} crops")

    print("Training XGBoost quantile regressors (low/median/high)...")
    models = train_models(df)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"models": models, "feature_order": FEATURE_ORDER}, MODEL_PATH)
    print(f"Models saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
