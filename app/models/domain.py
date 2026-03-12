from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from app.database import Base

class ClinicalRecord(Base):
    __tablename__ = "clinical_records"

    id = Column(Integer, primary_key=True, index=True)
    encrypted_symptoms = Column(String, nullable=False)
    predicted_disease = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    client_ip = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))