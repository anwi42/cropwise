import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from app.crop_config import CROP_SEASONS, CROP_WEATHER_RANGES, SEASON_ENCODING
from app.database import get_db_cursor

SAMPLES_PER_CROP_SEASON = 150
RANDOM_SEED = 42

MODELS_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODELS_DIR / "crop_recommendation_model.joblib"


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


def sample_uniform_with_margin(min_v: float, max_v: float, rng: np.random.Generator, margin: float = 0.15) -> float:
    span = max_v - min_v
    low = min_v - span * margin
    high = max_v + span * margin
    return float(rng.uniform(max(low, 0.0), high))


def generate_training_rows(standards: dict, rng: np.random.Generator) -> pd.DataFrame:
    records = []

    for crop, seasons in CROP_SEASONS.items():
        crop_standards = standards.get(crop)
        if not crop_standards:
            continue

        n_min, n_max = crop_standards["nitrogen"]
        p_min, p_max = crop_standards["phosphorus"]
        k_min, k_max = crop_standards["potassium"]
        ph_min, ph_max = crop_standards["ph"]
        oc_min, oc_max = crop_standards["organic_carbon"]
        rain_min, rain_max, temp_min, temp_max = CROP_WEATHER_RANGES[crop]

        for season in seasons:
            season_code = SEASON_ENCODING[season]
            for _ in range(SAMPLES_PER_CROP_SEASON):
                records.append(
                    {
                        "nitrogen": sample_uniform_with_margin(n_min, n_max, rng),
                        "phosphorus": sample_uniform_with_margin(p_min, p_max, rng),
                        "potassium": sample_uniform_with_margin(k_min, k_max, rng),
                        "ph": min(14.0, max(0.0, sample_uniform_with_margin(ph_min, ph_max, rng))),
                        "organic_carbon": max(0.0, sample_uniform_with_margin(oc_min, oc_max, rng)),
                        "season": season_code,
                        "rainfall": max(0.0, sample_uniform_with_margin(rain_min, rain_max, rng)),
                        "temperature": sample_uniform_with_margin(temp_min, temp_max, rng),
                        "crop": crop,
                    }
                )

    return pd.DataFrame.from_records(records)


def train_model(df: pd.DataFrame) -> lgb.LGBMClassifier:
    feature_cols = [
        "nitrogen",
        "phosphorus",
        "potassium",
        "ph",
        "organic_carbon",
        "season",
        "rainfall",
        "temperature",
    ]
    X = df[feature_cols]
    y = df["crop"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    model = lgb.LGBMClassifier(
        objective="multiclass",
        num_class=y.nunique(),
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=RANDOM_SEED,
        verbosity=-1,
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Test accuracy: {accuracy:.4f} on {len(X_test)} held-out samples")
    print(f"Classes: {list(model.classes_)}")

    return model


def main():
    rng = np.random.default_rng(RANDOM_SEED)

    print("Fetching ICAR soil standards from database...")
    standards = fetch_soil_standards()
    print(f"Loaded standards for {len(standards)} crops")

    print("Generating synthetic training data grounded in ICAR ranges + agronomic season/weather profiles...")
    df = generate_training_rows(standards, rng)
    print(f"Generated {len(df)} training rows across {df['crop'].nunique()} crops")

    print("Training LightGBM multiclass classifier...")
    model = train_model(df)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
