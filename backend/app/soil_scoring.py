from typing import Dict, Optional

NUTRIENT_LABELS = {
    "nitrogen": "Nitrogen",
    "phosphorus": "Phosphorus",
    "potassium": "Potassium",
    "ph": "Soil pH",
    "organic_carbon": "Organic Carbon",
}

RED_MAX = 40
YELLOW_MAX = 70


def score_nutrient(value: Optional[float], min_value: float, max_value: float) -> tuple:
    if value is None:
        return "missing", 0.0

    if min_value <= value <= max_value:
        return "optimal", 100.0

    if value < min_value:
        deficit_ratio = (min_value - value) / min_value if min_value > 0 else 1.0
        score = max(0.0, 100.0 - deficit_ratio * 100.0)
        return "deficient", round(score, 2)

    excess_ratio = (value - max_value) / max_value if max_value > 0 else 1.0
    score = max(0.0, 100.0 - excess_ratio * 100.0)
    return "excess", round(score, 2)


def build_explanation(
    nutrient: str,
    value: Optional[float],
    min_value: float,
    max_value: float,
    unit: str,
    status: str,
    crop: str,
) -> str:
    label = NUTRIENT_LABELS.get(nutrient, nutrient.title())

    if status == "missing":
        return f"{label} was not recorded for this soil report, so it could not be evaluated."

    if status == "optimal":
        return (
            f"{label} level ({value} {unit}) is within the ideal range "
            f"({min_value}-{max_value} {unit}) for {crop}. This is healthy, no action needed."
        )

    if status == "deficient":
        return (
            f"{label} level ({value} {unit}) is below the ideal range "
            f"({min_value}-{max_value} {unit}) for {crop}. Your soil needs more "
            f"{label.lower()} for good {crop} growth. Consider adding fertilizer "
            f"or organic matter to raise it."
        )

    return (
        f"{label} level ({value} {unit}) is above the ideal range "
        f"({min_value}-{max_value} {unit}) for {crop}. Excess {label.lower()} can "
        f"harm {crop} growth and wastes fertilizer cost. Avoid adding more of this "
        f"nutrient this season."
    )


def zone_for_score(health_score: int) -> str:
    if health_score <= RED_MAX:
        return "Red"
    if health_score <= YELLOW_MAX:
        return "Yellow"
    return "Green"


def compute_soil_health(
    soil_values: Dict[str, Optional[float]],
    standards: Dict[str, Dict[str, float]],
    crop: str,
) -> tuple:
    nutrient_details: Dict[str, dict] = {}
    nutrient_scores = []

    for nutrient, label in NUTRIENT_LABELS.items():
        value = soil_values.get(nutrient)
        standard = standards.get(nutrient)

        if standard is None:
            continue

        min_value = float(standard["min_value"])
        max_value = float(standard["max_value"])
        unit = standard["unit"]

        status, nutrient_score = score_nutrient(value, min_value, max_value)
        explanation = build_explanation(
            nutrient, value, min_value, max_value, unit, status, crop
        )

        nutrient_details[nutrient] = {
            "value": value,
            "ideal_min": min_value,
            "ideal_max": max_value,
            "unit": unit,
            "status": status,
            "nutrient_score": nutrient_score,
            "explanation": explanation,
        }
        nutrient_scores.append(nutrient_score)

    health_score = round(sum(nutrient_scores) / len(nutrient_scores)) if nutrient_scores else 0
    health_zone = zone_for_score(health_score)

    return health_score, health_zone, nutrient_details
