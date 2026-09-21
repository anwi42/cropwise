from functools import lru_cache
from pathlib import Path

import joblib

MODEL_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "ml_training"
    / "models"
    / "crop_recommendation_model.joblib"
)

FEATURE_ORDER = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "ph",
    "organic_carbon",
    "season",
    "rainfall",
    "temperature",
]


@lru_cache(maxsize=1)
def get_crop_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Crop recommendation model not found at {MODEL_PATH}. "
            "Run ml_training/generate_and_train_crop_model.py first."
        )
    return joblib.load(MODEL_PATH)


def predict_crop_probabilities(feature_values: list) -> dict:
    model = get_crop_model()
    probabilities = model.predict_proba([feature_values])[0]
    return dict(zip(model.classes_, probabilities))
