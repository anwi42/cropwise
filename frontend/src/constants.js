// Mirrors backend/app/crop_config.py and backend/app/yield_config.py so the
// dropdowns only ever send values the API's ICAR lookup tables recognize.
export const CROP_LIST = [
  'ajwain', 'bajra', 'barley', 'beetroot', 'bitter_gourd', 'bottle_gourd', 'brinjal', 'cabbage',
  'capsicum', 'carrot', 'castor', 'cauliflower', 'celery', 'chickpea', 'chilli', 'colocasia',
  'coriander', 'cotton', 'cowpea', 'cucumber', 'cumin', 'fennel', 'fenugreek', 'garlic', 'ginger',
  'groundnut', 'horse_gram', 'jute', 'leek', 'lentil', 'lettuce', 'linseed', 'maize', 'moong',
  'moth_bean', 'muskmelon', 'mustard', 'nigella', 'oats', 'okra', 'onion', 'peas', 'pigeonpea',
  'potato', 'pumpkin', 'radish', 'ragi', 'rajma', 'rice', 'ridge_gourd', 'safflower', 'sesame',
  'snake_gourd', 'sorghum', 'soybean', 'spinach', 'strawberry', 'sugarcane', 'sunflower',
  'sweet_potato', 'tobacco', 'tomato', 'turmeric', 'turnip', 'urad', 'watermelon', 'wheat', 'yam',
  'cluster_bean', 'ash_gourd', 'amaranthus', 'tinda', 'banana', 'papaya', 'pineapple',
]

export const CROP_LABELS = {
  ajwain: 'Ajwain',
  bajra: 'Bajra (Pearl Millet)',
  barley: 'Barley',
  beetroot: 'Beetroot',
  bitter_gourd: 'Bitter Gourd',
  bottle_gourd: 'Bottle Gourd',
  brinjal: 'Brinjal (Eggplant)',
  cabbage: 'Cabbage',
  capsicum: 'Capsicum',
  carrot: 'Carrot',
  castor: 'Castor (Arandi)',
  cauliflower: 'Cauliflower',
  celery: 'Celery',
  chickpea: 'Chickpea (Chana)',
  chilli: 'Chilli',
  colocasia: 'Colocasia (Arbi)',
  coriander: 'Coriander (Dhania)',
  cotton: 'Cotton',
  cowpea: 'Cowpea (Lobia)',
  cucumber: 'Cucumber',
  cumin: 'Cumin (Jeera)',
  fennel: 'Fennel (Saunf)',
  fenugreek: 'Fenugreek (Methi)',
  garlic: 'Garlic',
  ginger: 'Ginger',
  groundnut: 'Groundnut',
  horse_gram: 'Horse Gram (Kulthi)',
  jute: 'Jute',
  leek: 'Leek',
  lentil: 'Lentil (Masur)',
  lettuce: 'Lettuce',
  linseed: 'Linseed (Alsi)',
  maize: 'Maize',
  moong: 'Moong (Green Gram)',
  moth_bean: 'Moth Bean (Moth)',
  muskmelon: 'Muskmelon',
  mustard: 'Mustard (Sarson)',
  nigella: 'Nigella (Kalonji)',
  oats: 'Oats',
  okra: 'Okra (Bhindi)',
  onion: 'Onion',
  peas: 'Peas (Matar)',
  pigeonpea: 'Pigeonpea (Tur/Arhar)',
  potato: 'Potato',
  pumpkin: 'Pumpkin',
  radish: 'Radish',
  ragi: 'Ragi (Finger Millet)',
  rajma: 'Rajma (Kidney Bean)',
  rice: 'Rice',
  ridge_gourd: 'Ridge Gourd',
  safflower: 'Safflower (Kusum)',
  sesame: 'Sesame (Til)',
  snake_gourd: 'Snake Gourd',
  sorghum: 'Sorghum (Jowar)',
  soybean: 'Soybean',
  spinach: 'Spinach (Palak)',
  strawberry: 'Strawberry',
  sugarcane: 'Sugarcane',
  sunflower: 'Sunflower',
  sweet_potato: 'Sweet Potato',
  tobacco: 'Tobacco',
  tomato: 'Tomato',
  turmeric: 'Turmeric',
  turnip: 'Turnip',
  urad: 'Urad (Black Gram)',
  watermelon: 'Watermelon',
  wheat: 'Wheat',
  yam: 'Yam (Suran)',
  cluster_bean: 'Cluster Bean (Guar)',
  ash_gourd: 'Ash Gourd (Petha)',
  amaranthus: 'Amaranthus (Chaulai)',
  tinda: 'Tinda (Round Gourd)',
  banana: 'Banana',
  papaya: 'Papaya',
  pineapple: 'Pineapple',
}

// Sorted alphabetically by display label for the dropdowns.
export const CROP_OPTIONS = CROP_LIST
  .map((crop) => ({ value: crop, label: CROP_LABELS[crop] }))
  .sort((a, b) => a.label.localeCompare(b.label))

export const SEASON_OPTIONS = [
  { value: 'kharif', label: 'Kharif' },
  { value: 'rabi', label: 'Rabi' },
  { value: 'zaid', label: 'Zaid' },
]

export const BUDGET_OPTIONS = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
]

export const FARMING_METHOD_OPTIONS = [
  { value: 'conventional', label: 'Conventional' },
  { value: 'organic', label: 'Organic' },
  { value: 'mixed', label: 'Mixed' },
]

export const MARKET_RISK_VARIANT = {
  low: 'success',
  medium: 'warning',
  high: 'danger',
}

export const HEALTH_ZONE_VARIANT = {
  Green: 'success',
  Yellow: 'warning',
  Red: 'danger',
}

export const NUTRIENT_LABELS = {
  nitrogen: 'Nitrogen',
  phosphorus: 'Phosphorus',
  potassium: 'Potassium',
  ph: 'Soil pH',
  organic_carbon: 'Organic Carbon',
}

// Mirrors backend/app/orchard_config.py's ORCHARD_TREE_LIST/TREE_LABELS.
export const TREE_LABELS = {
  mango: 'Mango',
  banana: 'Banana',
  papaya: 'Papaya',
  guava: 'Guava',
  pomegranate: 'Pomegranate',
  citrus: 'Citrus (Orange/Lemon)',
  grapes: 'Grapes',
  coconut: 'Coconut',
}

export const TREE_OPTIONS = Object.entries(TREE_LABELS)
  .map(([value, label]) => ({ value, label }))
  .sort((a, b) => a.label.localeCompare(b.label))

// Mirrors the alert_type strings weather_alerts.py writes to the database.
export const ALERT_TYPE_META = {
  excess_rain_flowering: { label: 'Excess Rain', icon: 'CloudRain' },
  drought_grain_filling: { label: 'Drought Risk', icon: 'Sun' },
  frost_risk_seedling: { label: 'Frost Risk', icon: 'Snowflake' },
  high_humidity_fungal_risk: { label: 'Fungal Risk (Humidity)', icon: 'Droplets' },
}
