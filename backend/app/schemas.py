import re
from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.config import SUPPORTED_LANGUAGES
from app.crop_config import SUPPORTED_SEASONS
from app.orchard_config import ORCHARD_TREE_LIST
from app.yield_config import CROP_LIST, SOIL_TYPE_ENCODING

PHONE_REGEX = re.compile(r"^[6-9]\d{9}$")
VALID_INPUT_METHODS = {"manual", "ocr", "ocr_corrected"}


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str
    password: str = Field(..., min_length=6, max_length=72)
    preferred_language: str = "english"
    village: Optional[str] = None
    taluka: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    farm_size: Optional[float] = None
    soil_type: Optional[str] = None
    water_source: Optional[str] = None
    crops_grown_before: Optional[List[str]] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not PHONE_REGEX.match(v):
            raise ValueError(
                "phone must be a valid 10-digit Indian mobile number starting with 6-9"
            )
        return v

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        v_lower = v.lower()
        if v_lower not in SUPPORTED_LANGUAGES:
            raise ValueError(f"preferred_language must be one of {SUPPORTED_LANGUAGES}")
        return v_lower

    @field_validator("farm_size")
    @classmethod
    def validate_farm_size(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("farm_size must be greater than 0")
        return v

    @field_validator("soil_type")
    @classmethod
    def validate_soil_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_lower = v.strip().lower()
        if v_lower not in SOIL_TYPE_ENCODING:
            raise ValueError(f"soil_type must be one of {sorted(SOIL_TYPE_ENCODING)}")
        return v_lower


class RegisterResponse(BaseModel):
    success: bool
    message: str
    farmer_id: int


class LoginRequest(BaseModel):
    phone: str
    password: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not PHONE_REGEX.match(v):
            raise ValueError(
                "phone must be a valid 10-digit Indian mobile number starting with 6-9"
            )
        return v


class LoginResponse(BaseModel):
    success: bool
    message: str
    farmer_id: Optional[int] = None
    name: Optional[str] = None
    preferred_language: Optional[str] = None


class BankRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str
    password: str = Field(..., min_length=6, max_length=72)
    organization: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not PHONE_REGEX.match(v):
            raise ValueError(
                "phone must be a valid 10-digit Indian mobile number starting with 6-9"
            )
        return v


class BankRegisterResponse(BaseModel):
    success: bool
    message: str
    officer_id: int


class BankLoginRequest(BaseModel):
    phone: str
    password: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not PHONE_REGEX.match(v):
            raise ValueError(
                "phone must be a valid 10-digit Indian mobile number starting with 6-9"
            )
        return v


class BankLoginResponse(BaseModel):
    success: bool
    message: str
    officer_id: Optional[int] = None
    name: Optional[str] = None
    organization: Optional[str] = None


class BankFarmerSearchResponse(BaseModel):
    success: bool
    farmer_id: int
    name: str
    phone: str
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None


class BankSoilReportItem(BaseModel):
    id: int
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    ph: Optional[float] = None
    organic_carbon: Optional[float] = None
    health_score: Optional[int] = None
    health_zone: Optional[str] = None
    report_date: date


class BankYieldPredictionItem(BaseModel):
    id: int
    crop_type: str
    crop_variety: Optional[str] = None
    sowing_date: date
    predicted_yield_min: Optional[float] = None
    predicted_yield_max: Optional[float] = None
    confidence_score: Optional[float] = None
    created_at: datetime


class BankWeatherAlertItem(BaseModel):
    id: int
    alert_type: str
    alert_message: str
    created_at: datetime


class BankFarmerProfileResponse(BaseModel):
    success: bool
    farmer_id: int
    name: str
    phone: str
    village: Optional[str] = None
    taluka: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    farm_size: Optional[float] = None
    soil_type: Optional[str] = None
    water_source: Optional[str] = None
    crops_grown_before: Optional[List[str]] = None
    latest_soil_report: Optional[BankSoilReportItem] = None
    latest_yield_prediction: Optional[BankYieldPredictionItem] = None
    yield_prediction_history: List[BankYieldPredictionItem] = Field(default_factory=list)
    weather_alerts_history: List[BankWeatherAlertItem] = Field(default_factory=list)


class CertificateGenerateRequest(BaseModel):
    bank_officer_id: int
    farmer_id: int


class CertificateGenerateResponse(BaseModel):
    success: bool
    certificate_id: int
    verification_code: str
    document_hash: str
    pdf_download_url: str


class CertificateVerifyResponse(BaseModel):
    success: bool
    status: str
    certificate_id: int
    farmer_name: str
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    crop_type: str
    predicted_yield_min: float
    predicted_yield_max: float
    confidence_score: float
    soil_health_score: Optional[int] = None
    document_hash: str
    verification_code: str
    generated_at: datetime
    bank_officer_name: str


class LoanScoreRequest(BaseModel):
    bank_officer_id: int
    farmer_id: int


class LoanScoreBreakdownItem(BaseModel):
    category: str
    points_earned: int
    max_points: int
    reason: str


class LoanScoreResponse(BaseModel):
    success: bool
    farmer_id: int
    total_score: int
    risk_level: str
    breakdown: List[LoanScoreBreakdownItem]
    recommended_loan_min: float
    recommended_loan_max: float


CLAIM_REASONS = {"flood", "drought", "frost", "pest", "hailstorm", "fire"}


class ClaimVerifyRequest(BaseModel):
    bank_officer_id: int
    farmer_id: int
    claim_date: date
    claimed_loss_amount: float = Field(..., ge=0)
    claimed_reason: str

    @field_validator("claimed_reason")
    @classmethod
    def validate_claimed_reason(cls, v: str) -> str:
        v_lower = v.strip().lower()
        if v_lower not in CLAIM_REASONS:
            raise ValueError(f"claimed_reason must be one of {sorted(CLAIM_REASONS)}")
        return v_lower


class ClaimWeatherData(BaseModel):
    date: Optional[str] = None
    rainfall_mm: Optional[float] = None
    temp_max_c: Optional[float] = None
    temp_min_c: Optional[float] = None
    temp_mean_c: Optional[float] = None
    warning: Optional[str] = None


class ClaimYieldData(BaseModel):
    crop_type: str
    crop_variety: Optional[str] = None
    sowing_date: date
    predicted_yield_min: float
    predicted_yield_max: float
    confidence_score: float


class ClaimVerifyResponse(BaseModel):
    success: bool
    claim_verification_id: int
    verification_result: str
    explanation: str
    weather_data: ClaimWeatherData
    yield_data: Optional[ClaimYieldData] = None


class PortfolioFarmerItem(BaseModel):
    farmer_id: int
    name: str
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    crop_type: Optional[str] = None
    soil_health_score: Optional[int] = None
    soil_health_zone: Optional[str] = None
    active_weather_alerts: int
    predicted_yield_min: Optional[float] = None
    predicted_yield_max: Optional[float] = None
    risk_level: str


class PortfolioResponse(BaseModel):
    success: bool
    officer_id: int
    total_farmers: int
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int
    farmers: List[PortfolioFarmerItem]


class BankOverviewResponse(BaseModel):
    success: bool
    officer_id: int
    total_farmers_verified: int
    certificates_today: int
    high_risk_farmers: int
    pending_claim_verifications: int


class SoilFieldExtraction(BaseModel):
    value: Optional[float]
    confidence: float
    raw_text: Optional[str]
    needs_manual_correction: bool


class SoilOCRResponse(BaseModel):
    success: bool
    extracted_values: Dict[str, SoilFieldExtraction]
    needs_manual_review: bool


class SoilManualRequest(BaseModel):
    farmer_id: int
    nitrogen: float = Field(..., ge=0, le=2000)
    phosphorus: float = Field(..., ge=0, le=2000)
    potassium: float = Field(..., ge=0, le=2000)
    ph: float = Field(..., ge=0, le=14)
    organic_carbon: float = Field(..., ge=0, le=100)
    report_date: date
    input_method: str = "manual"

    @field_validator("input_method")
    @classmethod
    def validate_input_method(cls, v: str) -> str:
        v_lower = v.lower()
        if v_lower not in VALID_INPUT_METHODS:
            raise ValueError(f"input_method must be one of {sorted(VALID_INPUT_METHODS)}")
        return v_lower


class SoilManualResponse(BaseModel):
    success: bool
    message: str
    soil_report_id: int


class SoilScoreRequest(BaseModel):
    farmer_id: int
    soil_report_id: int
    crop_planned: str = Field(..., min_length=2, max_length=100)

    @field_validator("crop_planned")
    @classmethod
    def normalize_crop(cls, v: str) -> str:
        return v.strip().lower()


class NutrientScoreDetail(BaseModel):
    value: Optional[float]
    ideal_min: float
    ideal_max: float
    unit: str
    status: str
    nutrient_score: float
    explanation: str


class SoilScoreResponse(BaseModel):
    success: bool
    soil_report_id: int
    crop_planned: str
    health_score: int
    health_zone: str
    nutrient_details: Dict[str, NutrientScoreDetail]


SUPPORTED_BUDGETS = {"low", "medium", "high"}
SUPPORTED_FARMING_METHODS = {"conventional", "organic", "mixed"}


class CropRecommendRequest(BaseModel):
    farmer_id: int
    soil_report_id: int
    season: str
    budget: Optional[str] = None
    crop_preference: Optional[str] = Field(default=None, max_length=100)

    @field_validator("season")
    @classmethod
    def validate_season(cls, v: str) -> str:
        v_lower = v.strip().lower()
        if v_lower not in SUPPORTED_SEASONS:
            raise ValueError(f"season must be one of {SUPPORTED_SEASONS}")
        return v_lower

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_lower = v.strip().lower()
        if v_lower not in SUPPORTED_BUDGETS:
            raise ValueError(f"budget must be one of {sorted(SUPPORTED_BUDGETS)}")
        return v_lower

    @field_validator("crop_preference")
    @classmethod
    def normalize_crop_preference(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_stripped = v.strip()
        return v_stripped or None


class WeatherInfo(BaseModel):
    rainfall_mm: float
    avg_temperature_c: float
    source: str
    fallback_used: bool
    warning: Optional[str] = None
    timestamp: str


class CropRecommendationItem(BaseModel):
    crop_name: str
    reasoning: str
    soil_fit_score: int
    market_risk: str
    model_confidence: float


class CropRecommendResponse(BaseModel):
    success: bool
    crop_recommendation_id: int
    season: str
    weather: WeatherInfo
    recommendations: List[CropRecommendationItem]


class FertilizerRequest(BaseModel):
    farmer_id: int
    soil_report_id: int
    selected_crop: str = Field(..., min_length=2, max_length=100)
    sowing_date: Optional[date] = None
    farming_method: Optional[str] = None

    @field_validator("selected_crop")
    @classmethod
    def normalize_crop(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("farming_method")
    @classmethod
    def validate_farming_method(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_lower = v.strip().lower()
        if v_lower not in SUPPORTED_FARMING_METHODS:
            raise ValueError(f"farming_method must be one of {sorted(SUPPORTED_FARMING_METHODS)}")
        return v_lower


class FertilizerItem(BaseModel):
    nutrient: str
    status: str
    fertilizer_name: str
    chemical_name: str
    quantity_per_acre: float
    unit: str
    timing: str
    organic_alternative: str


class FertilizerResponse(BaseModel):
    success: bool
    fertilizer_prescription_id: int
    selected_crop: str
    soil_type_used: str
    items: List[FertilizerItem]
    excess_nutrient_warnings: List[str]
    message: str
    pdf_download_url: str


class OrchardAdvisoryRequest(BaseModel):
    farmer_id: int
    tree_type: str
    variety: Optional[str] = Field(default=None, max_length=100)
    planting_date: date
    tree_count: Optional[int] = Field(default=None, gt=0)
    area_acres: Optional[float] = Field(default=None, gt=0)

    @field_validator("tree_type")
    @classmethod
    def validate_tree_type(cls, v: str) -> str:
        v_lower = v.strip().lower()
        if v_lower not in ORCHARD_TREE_LIST:
            raise ValueError(f"tree_type must be one of {ORCHARD_TREE_LIST}")
        return v_lower

    @field_validator("planting_date")
    @classmethod
    def validate_planting_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("planting_date cannot be in the future")
        return v


class OrchardCareItem(BaseModel):
    irrigation: str
    pruning: str
    fertigation: str
    pest_watch: str


class OrchardAdvisoryResponse(BaseModel):
    success: bool
    orchard_crop_id: int
    tree_type: str
    variety: Optional[str] = None
    growth_stage: str
    years_since_planting: float
    weather: WeatherInfo
    care: OrchardCareItem
    weather_warnings: List[str]
    message: str


class YieldPredictRequest(BaseModel):
    farmer_id: int
    crop_type: str = Field(..., min_length=2, max_length=100)
    crop_variety: str = Field(..., min_length=1, max_length=100)
    sowing_date: date

    @field_validator("crop_type")
    @classmethod
    def validate_crop_type(cls, v: str) -> str:
        v_lower = v.strip().lower()
        if v_lower not in CROP_LIST:
            raise ValueError(f"crop_type must be one of {CROP_LIST}")
        return v_lower


class YieldWeatherInfo(BaseModel):
    rainfall_mm: float
    avg_temperature_c: float
    avg_humidity_pct: float
    source: str
    fallback_used: bool
    warning: Optional[str] = None
    timestamp: str


class YieldPredictResponse(BaseModel):
    success: bool
    yield_prediction_id: int
    crop_type: str
    crop_variety: str
    season: str
    weather: YieldWeatherInfo
    soil_fit_score: int
    predicted_yield_min: float
    predicted_yield_max: float
    confidence_score: float
    message: str


class WeatherAlertItem(BaseModel):
    id: int
    alert_type: str
    alert_message: str
    created_at: datetime


class AlertsResponse(BaseModel):
    success: bool
    farmer_id: int
    alerts: List[WeatherAlertItem]


class AlertsCheckResponse(BaseModel):
    success: bool
    farmers_checked: int
    farmers_skipped_no_crop: int
    alerts_created: int
