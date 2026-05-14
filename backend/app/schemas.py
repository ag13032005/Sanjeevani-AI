from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


RiskLevel = Literal["Low", "Medium", "High"]


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    email: EmailStr


class UserPublic(BaseModel):
    id: str
    name: str
    email: EmailStr


class PredictionResponse(BaseModel):
    risk: RiskLevel
    risk_level: RiskLevel
    disease: str
    explanation: str
    alert: str
    confidence: float
    recommendation: str
    inputs: dict
    feature_score: float
    location: str | None = None


class WeatherResponse(BaseModel):
    temperature: float
    humidity: float
    description: str
    wind_speed: float | None = None
    source: str


class AQIResponse(BaseModel):
    aqi: int
    category: str
    source: str


class HistoryItem(BaseModel):
    id: str
    location: str
    risk: RiskLevel
    risk_level: RiskLevel
    disease: str
    confidence: float
    recommendation: str
    temperature: float
    humidity: float
    aqi: float
    created_at: datetime


class PatientReportVitals(BaseModel):
    heart_rate: int
    bp_systolic: int
    bp_diastolic: int
    temperature: float
    spo2: float
    ecg: str
    bp: str
    heart_rate_status: str
    temperature_status: str
    bp_status: str
    spo2_status: str


class ReportPatient(BaseModel):
    name: str
    id: str
    date: str


class ReportDiagnosis(BaseModel):
    condition: str
    severity: str
    confidence: float


class HealthReportResponse(BaseModel):
    patient: ReportPatient
    vitals: PatientReportVitals
    diagnosis: ReportDiagnosis
    insights: list[str]
    alerts: list[str]
    recommendation: str


class MedicalReportCreate(BaseModel):
    patient_name: str = Field(min_length=2, max_length=120)
    age: int = Field(ge=0, le=120)
    heart_rate: int = Field(ge=0)
    bp_systolic: int = Field(ge=0)
    bp_diastolic: int = Field(ge=0)
    temperature: float
    spo2: float
    ecg: str = Field(min_length=1, max_length=120)
    notes: str = Field(default="", max_length=1000)


class ReportSummary(BaseModel):
    id: str
    patient_name: str
    age: int
    condition: str
    severity: str
    file_url: str | None = None
    created_at: datetime
    diagnosis: dict
    vitals: dict
    insights: list[str]
    alerts: list[str]
    recommendation: str


class IotPrediction(BaseModel):
    risk: RiskLevel
    disease: Literal["Dengue", "Flu", "Respiratory", "Normal"]
    confidence: float


class IotLiveResponse(BaseModel):
    timestamp: datetime
    vitals: dict
    cleaned_vitals: dict
    warnings: list[str]
    prediction: IotPrediction
    explanation: str
    alerts: list[str]
    recommendations: list[str]
