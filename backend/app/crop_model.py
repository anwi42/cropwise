from functools import lru_cache
from pathlib import Path

import joblib

from app.crop_traits import TRAIT_FIELDS, encode_traits

MODEL_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "ml_training"
    / "models"
    / "crop_recommendation_model.joblib"
)

OBSERVED_FEATURE_ORDER = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "ph",
    "organic_carbon",
    "season",
    "rainfall",
    "temperature",
]

# Trait fields are intrinsic to the crop being predicted, not something a
# farmer observes ahead of time - see predict_crop_fit_scores below.
FEATURE_ORDER = OBSERVED_FEATURE_ORDER + TRAIT_FIELDS


@lru_cache(maxsize=1)
def get_crop_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Crop recommendation model not found at {MODEL_PATH}. "
            "Run ml_training/generate_and_train_crop_model.py first."
        )
    return joblib.load(MODEL_PATH)


def predict_crop_fit_scores(observed_features: list, candidate_crops: list) -> dict:
    """Score each candidate crop by how well the observed conditions match it.

    The classifier was trained on [observed features] + [that row's own crop
    traits] -> crop label. At serving time we don't know which crop is
    correct yet (that's what we're trying to find out), so for each
    candidate we build the row as if that candidate were the answer - using
    its own known trait values - and read off the model's probability for
    that specific class. Candidates whose traits are inconsistent with the
    observed soil/weather conditions score low; a genuinely well-matched
    candidate scores high.
    """
    model = get_crop_model()
    class_index = {label: idx for idx, label in enumerate(model.classes_)}

    rows = []
    valid_candidates = []
    for crop in candidate_crops:
        if crop not in class_index:
            continue
        trait_values = encode_traits(crop)
        rows.append(observed_features + [trait_values[field] for field in TRAIT_FIELDS])
        valid_candidates.append(crop)

    if not rows:
        return {}

    probabilities = model.predict_proba(rows)
    return {
        crop: float(probabilities[i, class_index[crop]])
        for i, crop in enumerate(valid_candidates)
    }
