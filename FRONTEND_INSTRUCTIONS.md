# CropWise — React Frontend Instructions

## Project Overview
CropWise is an AI-powered agricultural intelligence platform
for Indian farmers. This is the React web frontend that
connects to the existing FastAPI backend running at
http://127.0.0.1:8000

## Tech Stack
- React 18
- Vite (for fast development)
- Tailwind CSS (styling)
- React Router v6 (navigation)
- Axios (API calls to backend)
- Recharts (charts and graphs)
- React Toastify (notifications)
- Lucide React (icons)

## Color Theme
Primary: Indigo (#4F46E5)
Primary Dark: (#3730A3)
Primary Light: (#EEF2FF)
Background: White (#FFFFFF)
Surface: (#F9FAFB)
Text Primary: (#111827)
Text Secondary: (#6B7280)
Success: (#10B981)
Warning: (#F59E0B)
Danger: (#EF4444)

## Project Structure
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Navbar.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Button.jsx
│   │   │   ├── Input.jsx
│   │   │   ├── Badge.jsx
│   │   │   └── Loader.jsx
│   │   └── features/
│   │       ├── SoilTest.jsx
│   │       ├── CropRecommendation.jsx
│   │       ├── FertilizerPrescription.jsx
│   │       ├── YieldPrediction.jsx
│   │       └── WeatherAlerts.jsx
│   ├── pages/
│   │   ├── Landing.jsx
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   └── dashboard/
│   │       ├── Overview.jsx
│   │       ├── SoilTestPage.jsx
│   │       ├── CropRecommendPage.jsx
│   │       ├── FertilizerPage.jsx
│   │       ├── YieldPage.jsx
│   │       └── AlertsPage.jsx
│   ├── services/
│   │   └── api.js
│   ├── context/
│   │   └── AuthContext.jsx
│   ├── App.jsx
│   └── main.jsx
├── index.html
├── tailwind.config.js
├── vite.config.js
└── package.json

---

## Pages — Detailed Instructions

### 1. Landing Page (/)
Full screen hero section:
- Top navbar: CropWise logo left, Login and
  Register buttons right
- Hero section center:
  Large heading: "Smart Farming Starts Here"
  Subheading: "AI-powered crop advisory, soil
  analysis, yield prediction and pest detection
  for Indian farmers"
  Two CTA buttons: "Get Started" (indigo filled)
  and "Learn More" (indigo outline)
- Three feature highlight cards below hero:
  Card 1: Soil Analysis icon + "Know Your Soil"
  Card 2: Crop AI icon + "Grow The Right Crop"
  Card 3: Weather icon + "Stay One Step Ahead"
- Footer: CropWise © 2026

Design notes:
- Hero background: very light indigo (#EEF2FF)
- Cards: white with subtle shadow
- Clean, minimal, no clutter
- Professional font sizes

---

### 2. Register Page (/register)
Centered card on white background:
- CropWise logo at top
- Heading: "Create Your Account"
- Form fields:
  Full Name (text input)
  Phone Number (text input)
  Password (password input)
  Village (text input)
  Taluka (text input)
  District (text input)
  State (dropdown — all Indian states)
  Farm Size in acres (number input)
  Soil Type (dropdown):
    Clay, Sandy, Loamy, Black Cotton,
    Red Laterite
  Water Source (dropdown):
    Borewell, Canal, Rainwater, Drip Irrigation
  Crops Grown Before (multi select checkboxes):
    Wheat, Rice, Tomato, Onion, Soybean,
    Maize, Cotton, Sugarcane
  Preferred Language (dropdown):
    English, Hindi, Marathi, Telugu,
    Tamil, Punjabi, Gujarati, Kannada
- Register button (indigo, full width)
- "Already have an account? Login" link below
- On success: redirect to /login
- On error: show toast notification with error

API call: POST http://127.0.0.1:8000/api/register

---

### 3. Login Page (/login)
Centered card on light indigo background:
- CropWise logo at top
- Heading: "Welcome Back"
- Subheading: "Login to your farm dashboard"
- Form fields:
  Phone Number (text input)
  Password (password input)
- Login button (indigo, full width)
- "Don't have an account? Register" link below
- On success: save farmer_id to localStorage,
  redirect to /dashboard
- On error: show toast "Invalid credentials"

API call: POST http://127.0.0.1:8000/api/login

---

### 4. Dashboard Layout (/dashboard/*)
Persistent layout with two parts:

LEFT SIDEBAR (fixed, 260px wide):
- CropWise logo at top with small leaf icon
- Farmer name below logo (fetched from localStorage)
- Navigation menu items with icons:
  🏠 Overview
  🌱 Soil Test
  🌾 Crop Recommendation
  🧪 Fertilizer Prescription
  📊 Yield Prediction
  ⛅ Weather Alerts
- Active item: indigo background, white text
- Inactive: grey text, hover indigo light background
- Logout button at very bottom of sidebar

TOP NAVBAR (fixed, spans content area):
- Page title (changes based on current page)
- Right side: farmer name + avatar initials circle

CONTENT AREA (right of sidebar):
- Light grey background (#F9FAFB)
- White cards for content
- Padding 24px all sides
## Sidebar Behavior
- Default state: expanded (260px wide)
- Collapsed state: icon only (70px wide)
- Toggle button: small arrow on right edge of sidebar
  pointing left when expanded, right when collapsed
- Smooth animation: 300ms transition
- When collapsed: show only icons, no text
- Hover on icon when collapsed: show tooltip with
  feature name
- Content area automatically expands to fill
  remaining space when sidebar collapses
- Remember collapsed/expanded state in localStorage

---

### 5. Overview Page (/dashboard/overview)
First page farmer sees after login.

Top section — Welcome banner:
- "Good Morning, [Farmer Name] 👋"
- Subtext: "Here's what's happening on your farm today"
- Indigo gradient background banner

Stats row — 4 small cards in a row:
- Card 1: Soil Health Score
  Shows latest score out of 100
  Green/Yellow/Red color based on zone
- Card 2: Last Yield Prediction
  Shows last predicted yield range
- Card 3: Weather Alerts
  Shows count of unread alerts
  Red badge if alerts exist
- Card 4: Last Soil Test Date
  Shows date of last soil report uploaded

Feature cards grid (2x3 grid of cards):
Each card has:
- Icon (large, indigo colored)
- Feature name (bold)
- One line description
- "Open" button (indigo outline)

Card 1: 🌱 Soil Test
"Upload your soil report or enter manually"

Card 2: 🌾 Crop Recommendation
"Get AI powered crop suggestions for this season"

Card 3: 🧪 Fertilizer Prescription
"Know exactly what and how much to apply"

Card 4: 📊 Yield Prediction
"Predict your harvest 6-8 weeks in advance"

Card 5: ⛅ Weather Alerts
"Stay ahead of dangerous weather patterns"

Card 6: 📄 Download Reports
"Download your soil and yield reports as PDF"

---

### 6. Soil Test Page (/dashboard/soil)
Two tab layout at top:
Tab 1: "Upload Report" (OCR)
Tab 2: "Enter Manually"

TAB 1 — Upload Report:
- Large upload box with dashed border
  "Click to upload or drag and drop"
  "Supports JPG, PNG, PDF"
  Indigo upload icon in center
- After upload: shows preview of image
- "Extract Values" button (indigo)
- After extraction: shows table of extracted values
  Each row: Nutrient name | Extracted Value |
  Confidence | Edit button
  Low confidence rows highlighted in yellow
- "Confirm and Save" button

TAB 2 — Enter Manually:
- Clean form with fields:
  Nitrogen (kg/ha) — number input
  Phosphorus (kg/ha) — number input
  Potassium (kg/ha) — number input
  pH — number input (0-14)
  Organic Carbon (%) — number input
  Report Date — date picker
- "Save Soil Data" button (indigo)

After saving either tab:
- Show soil health score card immediately
- Large score number in center
- Color coded circle: Red/Yellow/Green
- Nutrient breakdown table below:
  Each nutrient: name, value, status, explanation
- "Get Crop Recommendation" button at bottom

API calls:
POST http://127.0.0.1:8000/api/soil/ocr
POST http://127.0.0.1:8000/api/soil/manual
POST http://127.0.0.1:8000/api/soil/score

---

### 7. Crop Recommendation Page (/dashboard/crops)
Top section — inputs:
- Season dropdown: Kharif, Rabi, Zaid
- "Get Recommendations" button (indigo)
- Uses latest soil report automatically

Results section (after API call):
- Three crop cards side by side
- Each card:
  Crop name (large, bold)
  Soil fit score — circular progress bar
  Market risk badge:
    Green = Low Risk
    Yellow = Medium Risk
    Red = High Risk
  Reasoning text below
  Card border: gold for rank 1,
  silver for rank 2, bronze for rank 3

Weather info card below crops:
- Shows current weather used for recommendation
- Temperature, rainfall, humidity

API call:
POST http://127.0.0.1:8000/api/crop/recommend

---

### 8. Fertilizer Prescription Page (/dashboard/fertilizer)
Top section — inputs:
- Select crop dropdown (from recommended crops
  or type manually)
- "Generate Prescription" button (indigo)
- Uses latest soil report automatically

Results section:
- Prescription table:
  Columns: Fertilizer | Chemical Name |
  Quantity/Acre | Timing | Organic Alternative
  Each row alternating white and light grey
- Warnings section below table:
  Yellow warning cards for any excess nutrients
- "No fertilizer needed" message if soil is optimal
  with green checkmark
- "Download PDF" button (indigo, prominent)
  Downloads prescription as PDF

API calls:
POST http://127.0.0.1:8000/api/soil/fertilizer
GET http://127.0.0.1:8000/api/soil/fertilizer/{id}/pdf

---

### 9. Yield Prediction Page (/dashboard/yield)
Top section — input form:
- Crop Type (text input or dropdown)
- Crop Variety (text input)
- Sowing Date (date picker)
- "Predict Yield" button (indigo)

Loading state:
- Spinner with message
  "Analyzing weather and soil data..."

Results section:
- Large prediction display card:
  Indigo gradient background
  "Expected Yield" label
  Large numbers: "3.2 — 4.1 tons/acre"
  Confidence score below: "Confidence: 78%"
- Two info cards below side by side:
  Left: Weather summary used
    (rainfall, temperature, humidity)
  Right: Soil summary used
    (NPK values, pH)
- Note at bottom:
  "Prediction accuracy improves after
  first full season of farm data"

API call:
POST http://127.0.0.1:8000/api/yield/predict

---

### 10. Weather Alerts Page (/dashboard/alerts)
Top section:
- "Run Weather Check" button (indigo outline)
  Manually triggers the weather check job
- Last checked timestamp shown

Alerts list:
- If no alerts: green card "No weather threats
  detected for your farm today" with checkmark
- If alerts exist: list of alert cards
  Each card:
    Alert type icon (rain/drought/frost/humidity)
    Alert message (bold)
    Timestamp
    Indigo left border on card
    "Mark as Read" button
  Unread alerts: white background
  Read alerts: light grey background

API calls:
POST http://127.0.0.1:8000/api/alerts/run-check
GET http://127.0.0.1:8000/api/alerts/{farmer_id}

---

## API Service (src/services/api.js)
Create axios instance with:
- baseURL: http://127.0.0.1:8000
- All API functions exported separately:
  registerFarmer(data)
  loginFarmer(data)
  uploadSoilOCR(formData)
  saveSoilManual(data)
  getSoilScore(data)
  getCropRecommendation(data)
  getFertilizerPrescription(data)
  downloadFertilizerPDF(prescriptionId)
  predictYield(data)
  runWeatherCheck()
  getAlerts(farmerId)

## Auth Context (src/context/AuthContext.jsx)
- Store farmer_id and farmer name in localStorage
- Provide login, logout functions
- Protected routes — redirect to /login
  if not logged in

## Important Rules
- Show loading spinner on every API call
- Show toast notification on every error
- Show success toast on every successful action
- All forms must have proper validation
  before API call
- Empty states for all lists
  (no alerts, no recommendations yet)
- Responsive design — works on desktop
  and tablet
- Never show raw API errors to user
  always show friendly message
- farmer_id stored in localStorage after login
  used in all subsequent API calls

## Build Order
1. Setup Vite + React + Tailwind + dependencies
2. Create api.js service file
3. Create AuthContext
4. Build Landing page
5. Build Register page
6. Build Login page
7. Build Dashboard layout with Sidebar
8. Build Overview page
9. Build Soil Test page
10. Build Crop Recommendation page
11. Build Fertilizer Prescription page
12. Build Yield Prediction page
13. Build Weather Alerts page
14. Connect all pages to backend APIs
15. Test complete flow end to end

## First Task for Claude Code
1. Create a new React app using Vite inside
   the frontend folder:
   npm create vite@latest frontend --
   --template react
2. Install all dependencies:
   npm install axios react-router-dom
   recharts react-toastify lucide-react
   tailwindcss @tailwindcss/vite
3. Configure Tailwind with indigo color theme
4. Set up React Router with all routes
5. Create api.js with axios instance and
   all API functions
6. Create AuthContext with login logout
   and protected routes
7. Build Landing page completely
8. Build Register and Login pages completely
9. Test registration and login work with
   the backend