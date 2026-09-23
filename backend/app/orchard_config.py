"""Orchard (perennial fruit tree) advisory configuration.

Unlike annual crops (see crop_stage_config.py), orchard trees are tracked by
years since planting rather than days after sowing, and once mature they
follow a recurring annual fruiting cycle instead of a single season.

Canonical stage names used across all tree types so a single advisory
routine can run for any of them:
  establishment      -> young tree, not yet bearing fruit
  vegetative_growth   -> mature tree, between fruiting cycles
  flowering            -> blossom / flower set, most rain-sensitive stage
  fruit_development    -> fruit sizing/filling, most drought-sensitive stage
  harvest              -> fruit ready to pick, most rain-damage-sensitive stage
  bearing               -> mature tree that fruits year-round (no distinct season)
"""

ORCHARD_TREE_LIST = [
    "mango", "banana", "papaya", "guava", "pomegranate", "citrus", "grapes", "coconut",
]

TREE_LABELS = {
    "mango": "Mango",
    "banana": "Banana",
    "papaya": "Papaya",
    "guava": "Guava",
    "pomegranate": "Pomegranate",
    "citrus": "Citrus (Orange/Lemon)",
    "grapes": "Grapes",
    "coconut": "Coconut",
}

# Years from planting until the tree first bears fruit.
TREE_MATURITY_YEARS = {
    "mango": 4,
    "banana": 1,
    "papaya": 1,
    "guava": 3,
    "pomegranate": 2,
    "citrus": 3,
    "grapes": 2,
    "coconut": 6,
}

# Trees whose stage depends on the actual calendar month (fixed annual
# flowering/harvest season).
CALENDAR_STAGE_TREES = {
    "mango": [
        ("flowering", 12, 2),
        ("fruit_development", 3, 4),
        ("harvest", 5, 6),
        ("vegetative_growth", 7, 11),
    ],
    "guava": [
        ("flowering", 3, 4),
        ("fruit_development", 5, 7),
        ("harvest", 8, 9),
        ("vegetative_growth", 10, 2),
    ],
    "pomegranate": [
        ("flowering", 1, 2),
        ("fruit_development", 3, 5),
        ("harvest", 6, 7),
        ("vegetative_growth", 8, 12),
    ],
    "citrus": [
        ("flowering", 2, 3),
        ("fruit_development", 4, 9),
        ("harvest", 10, 12),
        ("vegetative_growth", 1, 1),
    ],
    "grapes": [
        ("flowering", 12, 1),
        ("fruit_development", 2, 2),
        ("harvest", 3, 3),
        ("vegetative_growth", 4, 11),
    ],
}

# Trees that fruit on a repeating cycle counted from the month they first
# bear (months since first bearing, 1-indexed, wraps every cycle_length).
CYCLE_STAGE_TREES = {
    "banana": {
        "cycle_length": 12,
        "stages": [
            ("vegetative_growth", 1, 5),
            ("flowering", 6, 7),
            ("fruit_development", 8, 10),
            ("harvest", 11, 12),
        ],
    },
    "papaya": {
        "cycle_length": 12,
        "stages": [
            ("vegetative_growth", 1, 3),
            ("flowering", 4, 5),
            ("fruit_development", 6, 8),
            ("harvest", 9, 12),
        ],
    },
}

# Trees that fruit continuously year-round once mature (no distinct season).
YEAR_ROUND_TREES = {"coconut"}

STAGE_ADVISORY = {
    "establishment": {
        "irrigation": "Water young trees lightly every 3-4 days to keep the root zone moist without waterlogging; avoid letting the soil dry out completely.",
        "pruning": "Remove weak or crossing side shoots to train a single strong central stem; no fruit pruning needed yet.",
        "fertigation": "Apply a small, frequent dose of nitrogen-rich fertilizer (e.g. urea) every 6-8 weeks to support vegetative growth.",
        "pest_watch": "Check regularly for stem borers and termites near the base, and for aphids on new leaf flush.",
    },
    "vegetative_growth": {
        "irrigation": "Water deeply once a week (more often in hot, dry weather) to encourage healthy canopy growth.",
        "pruning": "Prune out dead, diseased, or overcrowded branches to open up the canopy for light and air before the next flowering cycle.",
        "fertigation": "Apply a balanced NPK dose now to build up reserves for the coming flowering season.",
        "pest_watch": "Watch for leaf-eating caterpillars and scale insects on new growth.",
    },
    "flowering": {
        "irrigation": "Keep irrigation steady but avoid overwatering or heavy flooding, which can cause flowers to drop.",
        "pruning": "Avoid pruning now; cutting during flowering removes the flush that will set fruit.",
        "fertigation": "Switch to a phosphorus- and potassium-rich fertilizer to support flower and fruit set.",
        "pest_watch": "Inspect flowers for thrips and mites, which can reduce fruit set if left untreated.",
    },
    "fruit_development": {
        "irrigation": "Maintain consistent soil moisture; drought stress during fruit sizing directly reduces final fruit weight.",
        "pruning": "Thin out excess or damaged fruit if the tree is overloaded, to improve size and quality of the remaining fruit.",
        "fertigation": "Continue potassium-rich fertigation to support fruit filling and improve sweetness.",
        "pest_watch": "Check developing fruit for fruit flies and borers; consider pheromone traps or bagging fruit if infestation is seen.",
    },
    "harvest": {
        "irrigation": "Reduce irrigation slightly in the days before picking to improve fruit quality and shelf life.",
        "pruning": "Light pruning of harvested branches can be done immediately after picking to shape the tree for the next cycle.",
        "fertigation": "Hold off on fertilizer until after harvest is complete, then apply a recovery dose.",
        "pest_watch": "Harvest promptly once ripe; overripe fruit left on the tree attracts fruit flies and birds.",
    },
    "bearing": {
        "irrigation": "Water deeply and regularly year-round; this tree fruits continuously and has no dormant season.",
        "pruning": "Remove dry fronds/leaves and any diseased material regularly to keep the tree healthy.",
        "fertigation": "Apply a balanced fertilizer dose every 2-3 months to sustain continuous fruiting.",
        "pest_watch": "Inspect regularly for scale insects, mites, and rot at the base, since there is no off-season lull to catch up on care.",
    },
}


def _month_in_range(month: int, start: int, end: int) -> bool:
    if start <= end:
        return start <= month <= end
    return month >= start or month <= end


def get_orchard_stage(tree_type: str, planting_date, today) -> str:
    """Return the canonical stage name for a tree on a given date.

    `planting_date` and `today` are `datetime.date` objects.
    """
    years_since_planting = (today - planting_date).days / 365.25
    maturity_years = TREE_MATURITY_YEARS.get(tree_type, 3)

    if years_since_planting < maturity_years:
        return "establishment"

    if tree_type in YEAR_ROUND_TREES:
        return "bearing"

    if tree_type in CALENDAR_STAGE_TREES:
        for stage_name, start_month, end_month in CALENDAR_STAGE_TREES[tree_type]:
            if _month_in_range(today.month, start_month, end_month):
                return stage_name
        return "vegetative_growth"

    if tree_type in CYCLE_STAGE_TREES:
        config = CYCLE_STAGE_TREES[tree_type]
        months_since_maturity = int(
            (years_since_planting - maturity_years) * 12
        )
        cycle_month = (months_since_maturity % config["cycle_length"]) + 1
        for stage_name, start_month, end_month in config["stages"]:
            if start_month <= cycle_month <= end_month:
                return stage_name
        return "vegetative_growth"

    return "vegetative_growth"
