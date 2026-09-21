SUPPORTED_SEASONS = ["kharif", "rabi", "zaid"]

SEASON_ENCODING = {"kharif": 0, "rabi": 1, "zaid": 2}

CROP_SEASONS = {
    "rice": ["kharif"],
    "maize": ["kharif", "rabi", "zaid"],
    "soybean": ["kharif"],
    "cotton": ["kharif"],
    "sugarcane": ["kharif", "rabi"],
    "wheat": ["rabi"],
    "onion": ["rabi", "kharif"],
    "tomato": ["kharif", "rabi", "zaid"],
}

CROP_WEATHER_RANGES = {
    "rice": (80.0, 250.0, 24.0, 35.0),
    "maize": (40.0, 150.0, 20.0, 32.0),
    "soybean": (60.0, 180.0, 22.0, 32.0),
    "cotton": (30.0, 120.0, 25.0, 35.0),
    "sugarcane": (60.0, 200.0, 24.0, 34.0),
    "wheat": (10.0, 60.0, 10.0, 22.0),
    "onion": (15.0, 80.0, 13.0, 28.0),
    "tomato": (20.0, 100.0, 18.0, 30.0),
}

MARKET_RISK = {
    "rice": "low",
    "wheat": "low",
    "maize": "medium",
    "soybean": "medium",
    "cotton": "high",
    "sugarcane": "medium",
    "onion": "high",
    "tomato": "high",
}
