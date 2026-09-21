"""Approximate ICAR-based crop growth-stage day ranges (days after sowing).

Stage names are canonical across crop types so a single alert-detection
routine can run for every crop:
  seedling      -> establishment, most frost-sensitive stage
  vegetative    -> canopy / root growth
  flowering     -> flowering, bulb initiation, or fruit set — most rain-sensitive stage
  grain_filling -> grain, bulb, or fruit filling — most drought-sensitive stage
  maturity      -> ripening, ready for harvest
"""

CROP_GROWTH_STAGES = {
    "wheat": [
        ("seedling", 0, 20),
        ("vegetative", 21, 55),
        ("flowering", 56, 75),
        ("grain_filling", 76, 110),
        ("maturity", 111, 140),
    ],
    "rice": [
        ("seedling", 0, 20),
        ("vegetative", 21, 55),
        ("flowering", 56, 80),
        ("grain_filling", 81, 110),
        ("maturity", 111, 140),
    ],
    "maize": [
        ("seedling", 0, 15),
        ("vegetative", 16, 45),
        ("flowering", 46, 60),
        ("grain_filling", 61, 90),
        ("maturity", 91, 110),
    ],
    "soybean": [
        ("seedling", 0, 15),
        ("vegetative", 16, 40),
        ("flowering", 41, 55),
        ("grain_filling", 56, 85),
        ("maturity", 86, 105),
    ],
    "cotton": [
        ("seedling", 0, 25),
        ("vegetative", 26, 60),
        ("flowering", 61, 100),
        ("grain_filling", 101, 140),
        ("maturity", 141, 170),
    ],
    "sugarcane": [
        ("seedling", 0, 40),
        ("vegetative", 41, 180),
        ("flowering", 181, 240),
        ("grain_filling", 241, 330),
        ("maturity", 331, 360),
    ],
    "onion": [
        ("seedling", 0, 25),
        ("vegetative", 26, 65),
        ("flowering", 66, 90),
        ("grain_filling", 91, 120),
        ("maturity", 121, 145),
    ],
    "tomato": [
        ("seedling", 0, 20),
        ("vegetative", 21, 40),
        ("flowering", 41, 60),
        ("grain_filling", 61, 90),
        ("maturity", 91, 110),
    ],
}

TOTAL_CROP_DURATION_DAYS = {
    crop: stages[-1][2] for crop, stages in CROP_GROWTH_STAGES.items()
}


def get_current_growth_stage(crop: str, days_after_sowing: int):
    for stage_name, min_day, max_day in CROP_GROWTH_STAGES.get(crop, []):
        if min_day <= days_after_sowing <= max_day:
            return stage_name
    return None
