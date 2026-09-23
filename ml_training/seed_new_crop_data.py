"""One-time seed script: inserts icar_soil_standards and
icar_fertilizer_guidelines rows for crops added after the initial DB seed.

Run once after adding a new crop to app.crop_config.CROP_SEASONS. Safe to
re-run: it deletes any existing rows for these crop names before inserting.
"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database import get_db_cursor

# nutrient -> (min, max, unit)
SOIL_STANDARDS = {
    "cluster_bean": {
        "nitrogen": (70.0, 160.0, "kg/ha"),
        "phosphorus": (18.0, 30.0, "kg/ha"),
        "potassium": (90.0, 190.0, "kg/ha"),
        "ph": (6.0, 8.0, "pH"),
        "organic_carbon": (0.30, 0.60, "%"),
    },
    "ash_gourd": {
        "nitrogen": (170.0, 330.0, "kg/ha"),
        "phosphorus": (15.0, 28.0, "kg/ha"),
        "potassium": (150.0, 270.0, "kg/ha"),
        "ph": (6.0, 7.5, "pH"),
        "organic_carbon": (0.50, 0.70, "%"),
    },
    "amaranthus": {
        "nitrogen": (180.0, 360.0, "kg/ha"),
        "phosphorus": (15.0, 28.0, "kg/ha"),
        "potassium": (140.0, 260.0, "kg/ha"),
        "ph": (6.0, 7.5, "pH"),
        "organic_carbon": (0.45, 0.75, "%"),
    },
    "tinda": {
        "nitrogen": (170.0, 330.0, "kg/ha"),
        "phosphorus": (15.0, 28.0, "kg/ha"),
        "potassium": (150.0, 270.0, "kg/ha"),
        "ph": (6.0, 7.0, "pH"),
        "organic_carbon": (0.50, 0.70, "%"),
    },
    "banana": {
        "nitrogen": (250.0, 500.0, "kg/ha"),
        "phosphorus": (20.0, 35.0, "kg/ha"),
        "potassium": (250.0, 500.0, "kg/ha"),
        "ph": (6.0, 7.5, "pH"),
        "organic_carbon": (0.60, 0.90, "%"),
    },
    "papaya": {
        "nitrogen": (200.0, 400.0, "kg/ha"),
        "phosphorus": (20.0, 35.0, "kg/ha"),
        "potassium": (200.0, 400.0, "kg/ha"),
        "ph": (6.0, 7.0, "pH"),
        "organic_carbon": (0.55, 0.85, "%"),
    },
    "pineapple": {
        "nitrogen": (200.0, 400.0, "kg/ha"),
        "phosphorus": (15.0, 30.0, "kg/ha"),
        "potassium": (280.0, 520.0, "kg/ha"),
        "ph": (4.5, 6.5, "pH"),
        "organic_carbon": (0.60, 0.90, "%"),
    },
}

LEGUME_TEMPLATE = {
    "Urea": (
        "Urea (46% N)",
        "Full dose as basal at sowing (starter dose, crop fixes remaining N)",
        "Farmyard manure 2 tons/acre + Rhizobium culture seed treatment",
    ),
    "DAP": (
        "Di-ammonium Phosphate (18-46-0)",
        "Full dose as basal at sowing",
        "Rock phosphate 35-40 kg/acre + PSB culture",
    ),
    "MOP": (
        "Muriate of Potash (60% K2O)",
        "Full dose as basal at sowing",
        "Wood ash 80-100 kg/acre",
    ),
}

VINE_VEGETABLE_TEMPLATE = {
    "Urea": (
        "Urea (46% N)",
        "50% basal, 50% at vine spread/flowering",
        "Vermicompost 1.5 tons/acre",
    ),
    "DAP": (
        "Di-ammonium Phosphate (18-46-0)",
        "Full dose as basal at sowing",
        "Bone meal 35 kg/acre",
    ),
    "MOP": (
        "Muriate of Potash (60% K2O)",
        "50% basal, 50% at fruit development",
        "Wood ash 90 kg/acre",
    ),
}

LEAFY_GREEN_TEMPLATE = {
    "Urea": (
        "Urea (46% N)",
        "Split into 3 doses after each cutting",
        "Vermicompost 1.2 tons/acre",
    ),
    "DAP": (
        "Di-ammonium Phosphate (18-46-0)",
        "Full dose as basal at sowing",
        "Bone meal 30 kg/acre",
    ),
    "MOP": (
        "Muriate of Potash (60% K2O)",
        "Full dose as basal at sowing",
        "Wood ash 70 kg/acre",
    ),
}

ORCHARD_FRUIT_TEMPLATE = {
    "Urea": (
        "Urea (46% N)",
        "Split into 4-6 doses through the growth cycle",
        "Farmyard manure 3-4 tons/acre",
    ),
    "DAP": (
        "Di-ammonium Phosphate (18-46-0)",
        "Full dose as basal at planting + one top-up mid-cycle",
        "Bone meal 45-60 kg/acre",
    ),
    "MOP": (
        "Muriate of Potash (60% K2O)",
        "Split into 4-6 doses, higher share at flowering/fruit development",
        "Wood ash 120-220 kg/acre",
    ),
}

# crop -> (template, {alluvial base quantity per acre for Urea, DAP, MOP})
FERTILIZER_PLAN = {
    "cluster_bean": (LEGUME_TEMPLATE, {"Urea": 12.0, "DAP": 40.0, "MOP": 12.0}),
    "ash_gourd": (VINE_VEGETABLE_TEMPLATE, {"Urea": 40.0, "DAP": 38.0, "MOP": 26.0}),
    "amaranthus": (LEAFY_GREEN_TEMPLATE, {"Urea": 50.0, "DAP": 35.0, "MOP": 20.0}),
    "tinda": (VINE_VEGETABLE_TEMPLATE, {"Urea": 40.0, "DAP": 38.0, "MOP": 26.0}),
    "banana": (ORCHARD_FRUIT_TEMPLATE, {"Urea": 150.0, "DAP": 90.0, "MOP": 150.0}),
    "papaya": (ORCHARD_FRUIT_TEMPLATE, {"Urea": 90.0, "DAP": 60.0, "MOP": 80.0}),
    "pineapple": (ORCHARD_FRUIT_TEMPLATE, {"Urea": 110.0, "DAP": 70.0, "MOP": 160.0}),
}

# Derived from the spread already observed across existing crops: red and
# loamy soils leach N/K faster and need more; black/clayey soils retain
# nutrients better and need less.
SOIL_TYPE_MULTIPLIERS = {
    "alluvial": {"Urea": 1.00, "DAP": 1.00, "MOP": 1.00},
    "black": {"Urea": 0.95, "DAP": 1.00, "MOP": 0.85},
    "clayey": {"Urea": 1.00, "DAP": 1.05, "MOP": 0.85},
    "loamy": {"Urea": 0.93, "DAP": 0.95, "MOP": 0.95},
    "red": {"Urea": 1.15, "DAP": 1.30, "MOP": 1.30},
}


def seed():
    crops = list(SOIL_STANDARDS.keys())
    assert set(crops) == set(FERTILIZER_PLAN.keys())

    with get_db_cursor(commit=True) as cur:
        cur.execute(
            "DELETE FROM icar_soil_standards WHERE crop_name = ANY(%s)", (crops,)
        )
        cur.execute(
            "DELETE FROM icar_fertilizer_guidelines WHERE crop_name = ANY(%s)", (crops,)
        )

        soil_rows = 0
        for crop, nutrients in SOIL_STANDARDS.items():
            for nutrient, (min_v, max_v, unit) in nutrients.items():
                cur.execute(
                    """
                    INSERT INTO icar_soil_standards (crop_name, nutrient, min_value, max_value, unit)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (crop, nutrient, min_v, max_v, unit),
                )
                soil_rows += 1

        fert_rows = 0
        for crop, (template, base_qty) in FERTILIZER_PLAN.items():
            for soil_type, multipliers in SOIL_TYPE_MULTIPLIERS.items():
                for fertilizer_name, (chemical_name, timing, organic_alt) in template.items():
                    qty = round(base_qty[fertilizer_name] * multipliers[fertilizer_name], 1)
                    cur.execute(
                        """
                        INSERT INTO icar_fertilizer_guidelines
                            (crop_name, soil_type, fertilizer_name, chemical_name,
                             quantity_per_acre, timing, organic_alternative)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (crop, soil_type, fertilizer_name, chemical_name, qty, timing, organic_alt),
                    )
                    fert_rows += 1

    print(f"Inserted {soil_rows} icar_soil_standards rows for {len(crops)} crops")
    print(f"Inserted {fert_rows} icar_fertilizer_guidelines rows for {len(crops)} crops")


if __name__ == "__main__":
    seed()
