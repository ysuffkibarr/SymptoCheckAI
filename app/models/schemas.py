from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SymptomRequest(BaseModel):
    symptoms: str

class EpidemicLogCreate(BaseModel):
    country: Optional[str] = "Türkiye"
    city: str
    district: str
    raw_symptoms: str
    diagnosed_disease: str
    confidence_score: float

class EpidemicLogResponse(BaseModel):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True