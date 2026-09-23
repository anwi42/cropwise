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


def predict_yield(feature_values: list, crop_range: tuple[float, float] | None = None) -> dict:
    bundle = get_yield_models()
    models = bundle["models"]
    row = [feature_values]

    low = float(models["low"].predict(row)[0])
    median = float(models["median"].predict(row)[0])
    high = float(models["high"].predict(row)[0])

    if crop_range is not None:
        # A single regressor is shared across every crop, whose realistic yields span
        # ~0.1-30 tons/acre. Clamp to the same bounds used when generating this crop's
        # training data so the model can't report yields far outside a plausible range.
        base_low, base_high = crop_range
        clamp_low, clamp_high = base_low * 0.5, base_high * 1.1
        low = max(clamp_low, min(clamp_high, low))
        median = max(clamp_low, min(clamp_high, median))
        high = max(clamp_low, min(clamp_high, high))

    if low > median:
        low = median
    if high < median:
        high = median

    return {"low": low, "median": median, "high": high}
