from functools import lru_cache
from pathlib import Path

import joblib

MODEL_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "ml_training"
    / "models"
    / "yield_models.joblib"
)


@lru_cache(maxsize=1)
def get_yield_models() -> dict:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Yield prediction models not found at {MODEL_PATH}. "
            "Run ml_training/generate_and_train_yield_model.py first."
        )
    return joblib.load(MODEL_PATH)


def predict_yield(feature_values: list) -> dict:
    bundle = get_yield_models()
    models = bundle["models"]
    row = [feature_values]

    low = float(models["low"].predict(row)[0])
    median = float(models["median"].predict(row)[0])
    high = float(models["high"].predict(row)[0])

    if low > median:
        low = median
    if high < median:
        high = median

    return {"low": low, "median": median, "high": high}
