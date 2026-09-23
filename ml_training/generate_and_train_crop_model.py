import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split

from app.crop_config import CROP_SEASONS, CROP_WEATHER_RANGES, SEASON_ENCODING
from app.crop_model import FEATURE_ORDER
from app.crop_traits import (
    CATEGORICAL_TRAIT_FIELDS,
    CROP_TRAITS,
    NUMERIC_TRAIT_FIELDS,
    TRAIT_ENCODINGS,
    TRAIT_FIELDS,
)
from app.database import get_db_cursor

SAMPLES_PER_CROP_SEASON = 150
RANDOM_SEED = 42

# Categorical traits are crop-intrinsic (e.g. a farmer's rough estimate of a
# crop's drought tolerance), so we keep them mostly-correct but inject a
# little label noise instead of a hard-coded constant per crop - a purely
# deterministic lookup would let the model memorize traits -> crop and
# report an unrealistic ~100% accuracy.
CATEGORICAL_NOISE_PROB = 0.10
NUMERIC_TRAIT_MARGIN = 0.10

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


def jitter_value(base_value: float, rng: np.random.Generator, relative_margin: float) -> float:
    spread = max(abs(base_value) * relative_margin, 1.0)
    return float(rng.uniform(base_value - spread, base_value + spread))


def sample_noisy_categorical(true_value: str, encoding: dict, rng: np.random.Generator) -> int:
    if rng.random() < CATEGORICAL_NOISE_PROB:
        other_values = [v for v in encoding if v != true_value]
        return encoding[rng.choice(other_values)]
    return encoding[true_value]


def sample_trait_features(crop: str, rng: np.random.Generator) -> dict:
    traits = CROP_TRAITS[crop]
    features = {}

    for field in NUMERIC_TRAIT_FIELDS:
        features[field] = jitter_value(traits[field], rng, NUMERIC_TRAIT_MARGIN)

    for field in CATEGORICAL_TRAIT_FIELDS:
        features[field] = sample_noisy_categorical(traits[field], TRAIT_ENCODINGS[field], rng)

    return features


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
                record = {
                    "nitrogen": sample_uniform_with_margin(n_min, n_max, rng),
                    "phosphorus": sample_uniform_with_margin(p_min, p_max, rng),
                    "potassium": sample_uniform_with_margin(k_min, k_max, rng),
                    "ph": min(14.0, max(0.0, sample_uniform_with_margin(ph_min, ph_max, rng))),
                    "organic_carbon": max(0.0, sample_uniform_with_margin(oc_min, oc_max, rng)),
                    "season": season_code,
                    "rainfall": max(0.0, sample_uniform_with_margin(rain_min, rain_max, rng)),
                    "temperature": sample_uniform_with_margin(temp_min, temp_max, rng),
                }
                record.update(sample_trait_features(crop, rng))
                record["crop"] = crop
                records.append(record)

    return pd.DataFrame.from_records(records)


def top_confused_pairs(y_test: pd.Series, predictions: np.ndarray, class_labels: list, top_n: int = 10) -> list:
    cm = confusion_matrix(y_test, predictions, labels=class_labels)
    pair_counts: dict = {}
    for i, true_label in enumerate(class_labels):
        for j, pred_label in enumerate(class_labels):
            if i == j or cm[i, j] == 0:
                continue
            key = frozenset((true_label, pred_label))
            pair_counts[key] = pair_counts.get(key, 0) + int(cm[i, j])

    ranked = sorted(pair_counts.items(), key=lambda item: item[1], reverse=True)[:top_n]
    return [(tuple(pair), count) for pair, count in ranked]


def fit_lgbm(X_train, y_train, num_class, categorical_cols):
    model = lgb.LGBMClassifier(
        objective="multiclass",
        num_class=num_class,
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=RANDOM_SEED,
        verbosity=-1,
    )
    if categorical_cols:
        model.fit(X_train, y_train, categorical_feature=categorical_cols)
    else:
        model.fit(X_train, y_train)
    return model


def train_model(df: pd.DataFrame, feature_cols: list) -> dict:
    # The trait fields are nominal categories encoded as small integers (e.g.
    # market_category 0-5). Whether LightGBM should treat them as plain
    # numeric or as pandas categoricals (its dedicated split algorithm) is
    # not a fixed choice for this dataset: depending on how many crops/
    # classes are in play, one encoding sometimes degenerates into "no
    # further splits with positive gain" on every round (near-random
    # accuracy) while the other trains fine - and which one fails flips
    # depending on the crop set. Rather than hard-code an encoding that can
    # silently rot next time a crop is added/removed, train both on the same
    # split and keep whichever one actually validates.
    categorical_cols = [c for c in CATEGORICAL_TRAIT_FIELDS if c in feature_cols]
    y = df["crop"]

    X_numeric = df[feature_cols]
    X_train_num, X_test_num, y_train, y_test = train_test_split(
        X_numeric, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    candidates = [("numeric", X_train_num, X_test_num, [])]

    if categorical_cols:
        X_cat = df[feature_cols].copy()
        for col in categorical_cols:
            X_cat[col] = X_cat[col].astype("category")
        X_train_cat = X_cat.loc[X_train_num.index]
        X_test_cat = X_cat.loc[X_test_num.index]
        candidates.append(("categorical", X_train_cat, X_test_cat, categorical_cols))

    best = None
    for encoding_name, X_train, X_test, cat_cols in candidates:
        model = fit_lgbm(X_train, y_train, y.nunique(), cat_cols)
        acc = accuracy_score(y_test, model.predict(X_test))
        print(f"  [{encoding_name} encoding] held-out accuracy: {acc:.4f}")
        if best is None or acc > best[0]:
            best = (acc, encoding_name, model, X_test)

    accuracy, chosen_encoding, model, X_test = best
    print(f"Selected '{chosen_encoding}' encoding for trait features (higher held-out accuracy).")

    predictions = model.predict(X_test)
    class_labels = list(model.classes_)
    confused_pairs = top_confused_pairs(y_test, predictions, class_labels)

    importances = sorted(
        zip(feature_cols, model.feature_importances_), key=lambda item: item[1], reverse=True
    )

    print(f"Test accuracy: {accuracy:.4f} on {len(X_test)} held-out samples")
    print(f"Classes: {class_labels}")
    print("\nTop 10 most confused crop pairs (held-out set):")
    for (crop_a, crop_b), count in confused_pairs:
        print(f"  {crop_a} <-> {crop_b}: {count} misclassifications")
    print("\nFeature importance (LightGBM gain-based split count):")
    for feature, importance in importances:
        print(f"  {feature}: {importance}")

    return {
        "model": model,
        "accuracy": accuracy,
        "confused_pairs": confused_pairs,
        "importances": importances,
    }


def main():
    rng = np.random.default_rng(RANDOM_SEED)

    print("Fetching ICAR soil standards from database...")
    standards = fetch_soil_standards()
    print(f"Loaded standards for {len(standards)} crops")

    print("Generating synthetic training data grounded in ICAR ranges + agronomic season/weather profiles...")
    df = generate_training_rows(standards, rng)
    print(f"Generated {len(df)} training rows across {df['crop'].nunique()} crops")

    print(f"Training LightGBM multiclass classifier on {len(FEATURE_ORDER)} features...")
    result = train_model(df, FEATURE_ORDER)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(result["model"], MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
