"""Agronomic trait profile for each of the 68 supported crops.

These attributes are intrinsic to the crop itself (not observations of a
particular farm), so they are used differently depending on the model:

- Yield prediction already takes ``crop`` as a known input, so these traits
  are looked up for that crop and added as extra regression features.
- Crop recommendation predicts the crop identity itself, so these traits
  cannot be observed ahead of time. Instead, ``crop_model.py`` builds one
  candidate feature row per crop (using that crop's own trait values) and
  reads off the model's confidence in that specific class - see
  ``predict_crop_fit_scores``.
"""

WATER_REQUIREMENT_ENCODING = {"low": 0, "medium": 1, "high": 2}
MARKET_CATEGORY_ENCODING = {
    "cereal": 0,
    "pulse": 1,
    "vegetable": 2,
    "fruit": 3,
    "spice": 4,
    "cash_crop": 5,
}
IRRIGATION_DEPENDENCY_ENCODING = {"rainfed": 0, "irrigated": 1, "both": 2}
HUMIDITY_PREFERENCE_ENCODING = {"low": 0, "medium": 1, "high": 2}
ALTITUDE_SUITABILITY_ENCODING = {"plains": 0, "hills": 1, "both": 2}
FROST_TOLERANCE_ENCODING = {"no": 0, "yes": 1}
DROUGHT_TOLERANCE_ENCODING = {"low": 0, "medium": 1, "high": 2}

TRAIT_ENCODINGS = {
    "water_requirement": WATER_REQUIREMENT_ENCODING,
    "market_category": MARKET_CATEGORY_ENCODING,
    "irrigation_dependency": IRRIGATION_DEPENDENCY_ENCODING,
    "humidity_preference": HUMIDITY_PREFERENCE_ENCODING,
    "altitude_suitability": ALTITUDE_SUITABILITY_ENCODING,
    "frost_tolerance": FROST_TOLERANCE_ENCODING,
    "drought_tolerance": DROUGHT_TOLERANCE_ENCODING,
}

CATEGORICAL_TRAIT_FIELDS = list(TRAIT_ENCODINGS.keys())
NUMERIC_TRAIT_FIELDS = ["growth_duration_days", "min_temp_tolerance", "max_temp_tolerance"]
TRAIT_FIELDS = [
    "water_requirement",
    "growth_duration_days",
    "min_temp_tolerance",
    "max_temp_tolerance",
    "market_category",
    "irrigation_dependency",
    "humidity_preference",
    "altitude_suitability",
    "frost_tolerance",
    "drought_tolerance",
]

# (water_requirement, growth_duration_days, min_temp_tolerance, max_temp_tolerance,
#  market_category, irrigation_dependency, humidity_preference, altitude_suitability,
#  frost_tolerance, drought_tolerance)
_RAW_TRAITS = {
    "rice": ("high", 120, 18.0, 38.0, "cereal", "both", "high", "plains", "no", "low"),
    "maize": ("medium", 100, 10.0, 35.0, "cereal", "both", "medium", "both", "no", "medium"),
    "soybean": ("medium", 100, 15.0, 35.0, "cash_crop", "rainfed", "medium", "plains", "no", "medium"),
    "cotton": ("medium", 180, 15.0, 40.0, "cash_crop", "both", "medium", "plains", "no", "medium"),
    "sugarcane": ("high", 330, 18.0, 40.0, "cash_crop", "irrigated", "high", "plains", "no", "low"),
    "wheat": ("medium", 120, 2.0, 30.0, "cereal", "both", "low", "plains", "yes", "medium"),
    "onion": ("medium", 110, 8.0, 32.0, "vegetable", "irrigated", "low", "plains", "no", "medium"),
    "tomato": ("medium", 90, 10.0, 34.0, "vegetable", "irrigated", "medium", "both", "no", "low"),
    "ajwain": ("low", 140, 8.0, 30.0, "spice", "rainfed", "low", "plains", "no", "high"),
    "bajra": ("low", 80, 15.0, 42.0, "cereal", "rainfed", "low", "plains", "no", "high"),
    "barley": ("low", 110, 0.0, 28.0, "cereal", "rainfed", "low", "both", "yes", "high"),
    "beetroot": ("medium", 70, 5.0, 27.0, "vegetable", "irrigated", "medium", "both", "yes", "low"),
    "bitter_gourd": ("medium", 70, 18.0, 36.0, "vegetable", "both", "high", "plains", "no", "low"),
    "bottle_gourd": ("medium", 65, 18.0, 36.0, "vegetable", "both", "high", "plains", "no", "low"),
    "brinjal": ("medium", 110, 15.0, 35.0, "vegetable", "both", "medium", "both", "no", "medium"),
    "cabbage": ("medium", 90, 4.0, 25.0, "vegetable", "irrigated", "medium", "both", "yes", "low"),
    "capsicum": ("medium", 100, 12.0, 30.0, "vegetable", "irrigated", "medium", "hills", "no", "low"),
    "carrot": ("medium", 90, 5.0, 27.0, "vegetable", "irrigated", "medium", "both", "yes", "low"),
    "castor": ("low", 150, 15.0, 40.0, "cash_crop", "rainfed", "low", "plains", "no", "high"),
    "cauliflower": ("medium", 105, 5.0, 23.0, "vegetable", "irrigated", "medium", "both", "yes", "low"),
    "celery": ("high", 120, 7.0, 24.0, "vegetable", "irrigated", "high", "hills", "no", "low"),
    "chickpea": ("low", 100, 5.0, 30.0, "pulse", "rainfed", "low", "plains", "yes", "high"),
    "chilli": ("medium", 150, 15.0, 35.0, "spice", "both", "medium", "both", "no", "medium"),
    "colocasia": ("high", 180, 18.0, 35.0, "vegetable", "both", "high", "both", "no", "low"),
    "coriander": ("low", 90, 8.0, 30.0, "spice", "rainfed", "low", "plains", "no", "medium"),
    "cowpea": ("low", 70, 15.0, 38.0, "pulse", "rainfed", "medium", "plains", "no", "high"),
    "cucumber": ("medium", 60, 15.0, 35.0, "vegetable", "both", "medium", "both", "no", "low"),
    "cumin": ("low", 110, 8.0, 30.0, "spice", "rainfed", "low", "plains", "no", "high"),
    "fennel": ("low", 150, 8.0, 28.0, "spice", "irrigated", "low", "plains", "no", "medium"),
    "fenugreek": ("low", 90, 8.0, 28.0, "spice", "rainfed", "low", "plains", "no", "medium"),
    "garlic": ("medium", 150, 5.0, 28.0, "vegetable", "irrigated", "low", "both", "yes", "medium"),
    "ginger": ("high", 240, 15.0, 32.0, "spice", "both", "high", "hills", "no", "low"),
    "groundnut": ("low", 120, 18.0, 36.0, "cash_crop", "rainfed", "medium", "plains", "no", "high"),
    "horse_gram": ("low", 100, 15.0, 36.0, "pulse", "rainfed", "low", "both", "no", "high"),
    "jute": ("high", 120, 20.0, 38.0, "cash_crop", "both", "high", "plains", "no", "low"),
    "leek": ("medium", 120, 5.0, 25.0, "vegetable", "irrigated", "medium", "both", "yes", "low"),
    "lentil": ("low", 110, 2.0, 28.0, "pulse", "rainfed", "low", "plains", "yes", "high"),
    "lettuce": ("high", 65, 2.0, 24.0, "vegetable", "irrigated", "medium", "both", "yes", "low"),
    "linseed": ("low", 130, 5.0, 28.0, "cash_crop", "rainfed", "low", "plains", "yes", "high"),
    "moong": ("low", 65, 18.0, 38.0, "pulse", "rainfed", "medium", "plains", "no", "high"),
    "moth_bean": ("low", 75, 20.0, 42.0, "pulse", "rainfed", "low", "plains", "no", "high"),
    "muskmelon": ("medium", 90, 18.0, 38.0, "fruit", "irrigated", "low", "plains", "no", "medium"),
    "mustard": ("low", 110, 5.0, 28.0, "cash_crop", "rainfed", "low", "plains", "yes", "high"),
    "nigella": ("low", 120, 8.0, 28.0, "spice", "rainfed", "low", "plains", "no", "medium"),
    "oats": ("medium", 110, 2.0, 26.0, "cereal", "both", "low", "both", "yes", "medium"),
    "okra": ("medium", 60, 18.0, 38.0, "vegetable", "both", "medium", "plains", "no", "medium"),
    "peas": ("medium", 90, 2.0, 25.0, "pulse", "irrigated", "medium", "both", "yes", "low"),
    "pigeonpea": ("low", 180, 15.0, 38.0, "pulse", "rainfed", "medium", "plains", "no", "high"),
    "potato": ("medium", 100, 4.0, 27.0, "vegetable", "irrigated", "medium", "both", "yes", "low"),
    "pumpkin": ("medium", 100, 18.0, 36.0, "vegetable", "both", "medium", "plains", "no", "medium"),
    "radish": ("medium", 45, 4.0, 27.0, "vegetable", "irrigated", "medium", "both", "yes", "low"),
    "ragi": ("low", 120, 12.0, 36.0, "cereal", "rainfed", "medium", "both", "no", "high"),
    "rajma": ("medium", 100, 8.0, 27.0, "pulse", "irrigated", "medium", "hills", "yes", "medium"),
    "ridge_gourd": ("medium", 70, 18.0, 36.0, "vegetable", "both", "high", "plains", "no", "low"),
    "safflower": ("low", 130, 5.0, 32.0, "cash_crop", "rainfed", "low", "plains", "no", "high"),
    "sesame": ("low", 90, 20.0, 40.0, "cash_crop", "rainfed", "low", "plains", "no", "high"),
    "snake_gourd": ("medium", 75, 18.0, 36.0, "vegetable", "both", "high", "plains", "no", "low"),
    "sorghum": ("low", 110, 15.0, 42.0, "cereal", "rainfed", "low", "plains", "no", "high"),
    "spinach": ("medium", 45, 5.0, 27.0, "vegetable", "irrigated", "medium", "both", "yes", "low"),
    "strawberry": ("high", 150, 2.0, 24.0, "fruit", "irrigated", "medium", "hills", "yes", "low"),
    "sunflower": ("low", 100, 10.0, 34.0, "cash_crop", "both", "low", "plains", "no", "medium"),
    "sweet_potato": ("low", 120, 15.0, 35.0, "vegetable", "rainfed", "medium", "plains", "no", "medium"),
    "tobacco": ("medium", 120, 12.0, 32.0, "cash_crop", "irrigated", "medium", "plains", "no", "low"),
    "turmeric": ("high", 240, 15.0, 34.0, "spice", "both", "high", "both", "no", "low"),
    "turnip": ("medium", 55, 4.0, 27.0, "vegetable", "irrigated", "medium", "both", "yes", "low"),
    "urad": ("low", 75, 18.0, 38.0, "pulse", "rainfed", "medium", "plains", "no", "high"),
    "watermelon": ("medium", 90, 18.0, 38.0, "fruit", "irrigated", "low", "plains", "no", "medium"),
    "yam": ("medium", 270, 18.0, 34.0, "vegetable", "rainfed", "high", "both", "no", "medium"),
    "cluster_bean": ("low", 75, 20.0, 44.0, "cash_crop", "rainfed", "low", "plains", "no", "high"),
    "ash_gourd": ("medium", 110, 18.0, 38.0, "vegetable", "both", "high", "plains", "no", "low"),
    "amaranthus": ("medium", 30, 15.0, 40.0, "vegetable", "irrigated", "medium", "both", "no", "low"),
    "tinda": ("medium", 65, 20.0, 40.0, "vegetable", "both", "medium", "plains", "no", "medium"),
    "banana": ("high", 330, 15.0, 38.0, "fruit", "irrigated", "high", "plains", "no", "low"),
    "papaya": ("medium", 270, 18.0, 38.0, "fruit", "irrigated", "medium", "plains", "no", "medium"),
    "pineapple": ("high", 450, 18.0, 36.0, "fruit", "irrigated", "high", "both", "no", "medium"),
}

CROP_TRAITS = {
    crop: dict(zip(TRAIT_FIELDS, values)) for crop, values in _RAW_TRAITS.items()
}


def encode_traits(crop: str) -> dict:
    """Return this crop's traits as a fully numeric feature dict."""
    traits = CROP_TRAITS[crop]
    encoded = dict(traits)
    for field, encoding in TRAIT_ENCODINGS.items():
        encoded[field] = encoding[traits[field]]
    return encoded
