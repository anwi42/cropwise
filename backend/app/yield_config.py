from datetime import date

from app.crop_config import CROP_SEASONS
from app.crop_traits import TRAIT_FIELDS

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
    "ajwain": (0.15, 0.3),
    "bajra": (0.5, 1.0),
    "barley": (0.8, 1.6),
    "beetroot": (3.5, 8.0),
    "bitter_gourd": (3.0, 7.0),
    "bottle_gourd": (5.0, 11.0),
    "brinjal": (5.0, 11.0),
    "cabbage": (6.0, 13.0),
    "capsicum": (3.5, 8.0),
    "carrot": (3.5, 8.0),
    "castor": (0.3, 0.65),
    "cauliflower": (4.5, 10.0),
    "celery": (3.0, 6.5),
    "chickpea": (0.35, 0.7),
    "chilli": (2.5, 5.5),
    "colocasia": (3.0, 7.0),
    "coriander": (0.3, 0.6),
    "cowpea": (0.25, 0.5),
    "cucumber": (3.5, 8.0),
    "cumin": (0.12, 0.28),
    "fennel": (0.25, 0.5),
    "fenugreek": (0.2, 0.45),
    "garlic": (2.0, 4.5),
    "ginger": (3.0, 7.0),
    "groundnut": (0.4, 0.85),
    "horse_gram": (0.15, 0.35),
    "jute": (0.35, 0.75),
    "leek": (2.5, 5.5),
    "lentil": (0.3, 0.6),
    "lettuce": (2.5, 5.5),
    "linseed": (0.2, 0.4),
    "moong": (0.2, 0.45),
    "moth_bean": (0.12, 0.3),
    "muskmelon": (4.0, 9.0),
    "mustard": (0.3, 0.65),
    "nigella": (0.1, 0.25),
    "oats": (0.7, 1.4),
    "okra": (3.0, 6.5),
    "peas": (0.35, 0.75),
    "pigeonpea": (0.3, 0.6),
    "potato": (4.0, 9.0),
    "pumpkin": (4.0, 9.0),
    "radish": (3.5, 8.0),
    "ragi": (0.4, 0.8),
    "rajma": (0.3, 0.65),
    "ridge_gourd": (3.5, 8.0),
    "safflower": (0.25, 0.5),
    "sesame": (0.15, 0.35),
    "snake_gourd": (3.0, 7.0),
    "sorghum": (0.6, 1.2),
    "spinach": (2.5, 5.5),
    "strawberry": (2.0, 4.5),
    "sunflower": (0.35, 0.7),
    "sweet_potato": (3.5, 8.0),
    "tobacco": (0.5, 1.1),
    "turmeric": (4.0, 8.0),
    "turnip": (3.5, 7.5),
    "urad": (0.2, 0.45),
    "watermelon": (6.0, 13.0),
    "yam": (4.0, 9.0),
    "cluster_bean": (2.0, 4.5),
    "ash_gourd": (6.0, 13.0),
    "amaranthus": (2.0, 4.5),
    "tinda": (3.0, 6.5),
    "banana": (10.0, 22.0),
    "papaya": (6.0, 14.0),
    "pineapple": (10.0, 20.0),
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
] + TRAIT_FIELDS


def derive_season_from_sowing_date(sowing_date: date) -> str:
    month = sowing_date.month
    if month in (6, 7, 8, 9):
        return "kharif"
    if month in (10, 11, 12):
        return "rabi"
    return "zaid"
