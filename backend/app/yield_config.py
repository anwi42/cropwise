from datetime import date

from app.crop_config import CROP_SEASONS

SOIL_TYPE_ENCODING = {
    "alluvial": 0,
    "black": 1,
    "clayey": 2,
    "loamy": 3,
    "red": 4,
}

CROP_LIST = sorted(CROP_SEASONS.keys())
CROP_ENCODING = {crop: idx for idx, crop in enumerate(CROP_LIST)}

BASE_YIELD_RANGE_TONS_PER_ACRE = {
    "wheat": (1.0, 2.0),
    "rice": (0.9, 1.8),
    "maize": (1.0, 2.2),
    "soybean": (0.4, 0.9),
    "cotton": (0.25, 0.6),
    "sugarcane": (12.0, 30.0),
    "onion": (4.0, 10.0),
    "tomato": (6.0, 15.0),
}

HUMIDITY_RANGE_BY_SEASON = {
    "kharif": (60.0, 90.0),
    "rabi": (35.0, 65.0),
    "zaid": (15.0, 45.0),
}

SOWING_DAY_OF_YEAR_RANGE_BY_SEASON = {
    "kharif": (152, 243),
    "rabi": (274, 334),
    "zaid": (32, 90),
}

FEATURE_ORDER = [
    "nitrogen",
    "phosphorus",
    "potassium",
    "ph",
    "organic_carbon",
    "soil_type",
    "farm_size",
    "rainfall",
    "avg_temperature",
    "avg_humidity",
    "crop",
    "sowing_day_of_year",
    "season",
]


def derive_season_from_sowing_date(sowing_date: date) -> str:
    month = sowing_date.month
    if month in (6, 7, 8, 9):
        return "kharif"
    if month in (10, 11, 12):
        return "rabi"
    return "zaid"
