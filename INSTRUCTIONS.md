# Agri Platform — AI Agricultural Intelligence Platform

## Project Overview
An AI-powered agricultural platform for Indian farmers.
Farmers can register, get soil health analysis, crop
recommendations, yield predictions, pest detection
and weather alerts — all in their local language.

## Project Structure
agri-platform/
├── backend/         # FastAPI + ML models
├── mobile/          # Flutter farmer app
├── dashboard/       # React dashboard (later)
└── ml_training/     # Jupyter notebooks for training

## Users
- Farmers (mobile app) — primary users right now
- Banks (web dashboard) — later
- Agri Scientists (web dashboard) — later

---

## Tech Stack

### Backend
- FastAPI (Python)
- PostgreSQL (database)
- bcrypt (password hashing)
- EasyOCR (soil report OCR)
- YOLOv8 (pest detection)
- LightGBM (crop recommendation)
- XGBoost (yield prediction)
- IndicTrans2 (multilingual translation)

### Mobile
- Flutter (Android app for farmers)

### External APIs (all free, no registration needed)
- Open-Meteo (weather data — no API key needed)

---

## Database Schema

### districts table
```sql
CREATE TABLE districts (
    id SERIAL PRIMARY KEY,
    district_name VARCHAR(100),
    state VARCHAR(100),
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6)
);
```

### farmers table
```sql
CREATE TABLE farmers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    preferred_language VARCHAR(20) DEFAULT 'english',
    village VARCHAR(100),
    taluka VARCHAR(100),
    district VARCHAR(100),
    state VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### farms table
```sql
CREATE TABLE farms (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(id),
    farm_size DECIMAL(10,2),
    soil_type VARCHAR(50),
    water_source VARCHAR(50),
    crops_grown_before TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### soil_reports table
```sql
CREATE TABLE soil_reports (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(id),
    nitrogen DECIMAL(10,2),
    phosphorus DECIMAL(10,2),
    potassium DECIMAL(10,2),
    ph DECIMAL(4,2),
    organic_carbon DECIMAL(10,2),
    health_score INTEGER,
    health_zone VARCHAR(10),
    report_date DATE,
    input_method VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### crop_recommendations table
```sql
CREATE TABLE crop_recommendations (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(id),
    soil_report_id INTEGER REFERENCES soil_reports(id),
    recommended_crops JSONB,
    season VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### fertilizer_prescriptions table
```sql
CREATE TABLE fertilizer_prescriptions (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(id),
    soil_report_id INTEGER REFERENCES soil_reports(id),
    selected_crop VARCHAR(100),
    prescription JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### yield_predictions table
```sql
CREATE TABLE yield_predictions (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(id),
    crop_type VARCHAR(100),
    crop_variety VARCHAR(100),
    sowing_date DATE,
    predicted_yield_min DECIMAL(10,2),
    predicted_yield_max DECIMAL(10,2),
    confidence_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### pest_detections table
```sql
CREATE TABLE pest_detections (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(id),
    pest_name VARCHAR(100),
    severity VARCHAR(20),
    confidence_score DECIMAL(5,2),
    treatment_given JSONB,
    photo_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### weather_alerts table
```sql
CREATE TABLE weather_alerts (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER REFERENCES farmers(id),
    alert_message TEXT,
    alert_type VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### icar_soil_standards table
```sql
CREATE TABLE icar_soil_standards (
    id SERIAL PRIMARY KEY,
    crop_name VARCHAR(100),
    nutrient VARCHAR(50),
    min_value DECIMAL(10,2),
    max_value DECIMAL(10,2),
    unit VARCHAR(20)
);
```

### icar_fertilizer_guidelines table
```sql
CREATE TABLE icar_fertilizer_guidelines (
    id SERIAL PRIMARY KEY,
    crop_name VARCHAR(100),
    soil_type VARCHAR(50),
    fertilizer_name VARCHAR(100),
    chemical_name VARCHAR(100),
    quantity_per_acre DECIMAL(10,2),
    timing VARCHAR(255),
    organic_alternative VARCHAR(255)
);
```

### agri_glossary table
```sql
CREATE TABLE agri_glossary (
    id SERIAL PRIMARY KEY,
    term_english VARCHAR(100),
    hindi VARCHAR(100),
    marathi VARCHAR(100),
    telugu VARCHAR(100),
    tamil VARCHAR(100),
    punjabi VARCHAR(100),
    gujarati VARCHAR(100),
    kannada VARCHAR(100)
);
```

---

## Features To Build — Farmer Module

### Feature 1 — Registration + Login

POST /api/register
- Takes: name, phone, password, village, taluka,
  district, state, farm_size, soil_type,
  water_source, crops_grown_before, preferred_language
- Hashes password with bcrypt
- Saves to farmers table and farms table
- Returns: success message + farmer_id

POST /api/login
- Takes: phone, password
- Verifies against database
- Returns: success + farmer_id or invalid credentials

### Feature 2 — Soil Test OCR + Manual Entry

POST /api/soil/ocr
- Takes: image file of soil test report
- Preprocesses image with OpenCV
  (deskew, enhance contrast, remove noise)
- Runs EasyOCR on preprocessed image
- Extracts: nitrogen, phosphorus, potassium,
  ph, organic_carbon
- Returns: extracted values with confidence
  score per field
- Fields with confidence below 70% flagged
  for manual correction

POST /api/soil/manual
- Takes: farmer_id, nitrogen, phosphorus,
  potassium, ph, organic_carbon,
  report_date, input_method
- Saves to soil_reports table
- Returns: success + soil_report_id

### Feature 3 — Soil Health Score

POST /api/soil/score
- Takes: farmer_id, soil_report_id, crop_planned
- Fetches soil values from soil_reports table
- Compares each value against icar_soil_standards
  table for that specific crop
- Calculates score out of 100
- Assigns zone:
  Red = 0 to 40 (serious problems)
  Yellow = 41 to 70 (moderate issues)
  Green = 71 to 100 (healthy)
- Generates plain language explanation per nutrient
- Translates explanation to farmer preferred language
- Updates health_score and health_zone in soil_reports
- Returns: score, zone, explanation per nutrient

### Feature 4 — Crop Recommendation

POST /api/crop/recommend
- Takes: farmer_id, soil_report_id, season
- Fetches soil values from database
- Fetches farmer district from database
- Calls Open-Meteo API with district coordinates
  from districts lookup table
- Runs LightGBM model with inputs:
  nitrogen, phosphorus, potassium, ph,
  organic_carbon, season, rainfall, temperature
- Returns top 3 crops with:
  crop name, reasoning, soil fit score,
  market risk (high/medium/low)
- Saves to crop_recommendations table
- Translates output to farmer preferred language

### Feature 5 — Fertilizer Prescription

POST /api/soil/fertilizer
- Takes: farmer_id, soil_report_id, selected_crop
- Fetches soil values from database
- Looks up icar_fertilizer_guidelines table
  for that crop and soil type combination
- Identifies which nutrients are deficient
- Generates prescription:
  fertilizer chemical name, quantity per acre,
  timing, organic alternative
- Translates to farmer preferred language
- Saves to fertilizer_prescriptions table
- Generates downloadable PDF with large text,
  simple language, generic chemical names
- Returns: prescription details + PDF download link

### Feature 6 — Yield Prediction

POST /api/yield/predict
- Takes: farmer_id, crop_type, crop_variety, sowing_date
- Fetches soil data from soil_reports table
- Fetches farmer district from farmers table
- Calls Open-Meteo API for:
  historical weather last 6 months
  forecast next 14 days
  for farmer district coordinates
- Features fed to XGBoost model:
  nitrogen, phosphorus, potassium, ph,
  organic_carbon, soil_type, farm_size,
  rainfall_total, avg_temperature,
  avg_humidity, crop_type, crop_variety,
  sowing_date, season
- Returns:
  predicted_yield_min (tons per acre)
  predicted_yield_max (tons per acre)
  confidence_score
- Saves to yield_predictions table
- Translates output to farmer preferred language

### Feature 7 — Weather Alerts

Background job runs every day at 5am:
- Fetches all active farmers from database
- For each farmer fetches their district
- Calls Open-Meteo API for 14 day forecast
- Checks for dangerous patterns:
  excess rain during flowering stage
  drought during grain filling stage
  frost risk during seedling stage
  high humidity causing fungal disease risk
- If dangerous pattern found creates alert
  in weather_alerts table with crop aware message

GET /api/alerts/{farmer_id}
- Returns all unread alerts for that farmer
- Marks alerts as read after fetching
- Translates alerts to farmer preferred language

### Feature 8 — Pest Detection + Treatment

POST /api/pest/detect
- Takes: farmer_id, image file of affected crop
- Preprocesses image with OpenCV
- Runs YOLOv8 model trained on IP102 dataset
- Returns:
  pest_name
  confidence_score
  severity (early / moderate / severe)
  safety_precautions (shown first always)
  pesticide_chemical_name
  dosage_per_acre
  how_to_spray
  pre_harvest_interval_days
  organic_alternative
- If confidence below 60 percent flag for
  agri scientist review later
- Saves detection to pest_detections table
- Translates output to farmer preferred language
- Pesticide data from CIB and RC database
  stored locally — no internet needed

### Feature 9 — Multilingual Translation

Translation middleware applied to all API responses:
- Fetches farmer preferred_language from database
- Runs output text through IndicTrans2 model
- Checks agri_glossary table and overrides
  domain specific terms with verified translations
- Supported languages:
  english, hindi, marathi, telugu, tamil,
  punjabi, gujarati, kannada
- Applied automatically to all responses

---

## Important Rules
- All passwords hashed with bcrypt never plain text
- Every API response translated to farmer preferred language
- Confidence scores shown for all ML predictions
- If Open-Meteo API fails show cached weather
  data with warning never crash
- All amounts in metric units acres kg tons
- District name used for location — system
  internally converts to coordinates using
  districts lookup table
- Safety precautions always shown before
  pesticide dosage in pest treatment
- Show timestamp on all weather data

---

## Build Order
Build and test each feature completely before moving to next:
1. Registration + Login
2. Soil OCR + Manual Entry
3. Soil Health Score
4. Crop Recommendation
5. Fertilizer Prescription + PDF
6. Yield Prediction
7. Weather Alerts background job
8. Pest Detection + Treatment
9. Multilingual wrapper

---

## Environment Variables (.env file)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=agriplatform
DB_USER=postgres
DB_PASSWORD=your_password_here

---

## First Task
1. Create virtual environment inside backend folder
2. Install these packages:
   fastapi uvicorn psycopg2-binary bcrypt
   python-dotenv easyocr opencv-python
   lightgbm xgboost scikit-learn
   ultralytics pandas numpy requests
   reportlab python-multipart
3. Create .env file with database credentials
4. Connect to PostgreSQL and create
   database called agriplatform
5. Create all tables from schema above
6. Populate icar_soil_standards table
   with standard NPK and pH ranges
   for these crops:
   wheat, rice, tomato, onion, soybean,
   maize, cotton, sugarcane
7. Populate icar_fertilizer_guidelines table
   with fertilizer recommendations for same crops
8. Populate agri_glossary table with
   agricultural terms in all 8 languages
9. Build Feature 1 Registration and Login APIs
10. Test both APIs work correctly with sample data