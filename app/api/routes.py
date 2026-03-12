from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
from pathlib import Path

from app.limiter import limiter
from app.models.schemas import SymptomRequest
from app.services.ml_service import SymptomClassifier
from app.logger import logger
from app.security import encrypt_data
from app.database import get_db
from app.models.domain import ClinicalRecord 

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
csv_path = BASE_DIR / "data" / "DiseaseAndSymptoms.csv"
model_path = BASE_DIR / "data" / "semantic_cache.pkl"
index_path = BASE_DIR / "static" / "index.html"

classifier = SymptomClassifier(str(csv_path), str(model_path))

@router.get("/", response_class=HTMLResponse)
async def root():
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@router.post("/api/analyze")
@limiter.limit("5/minute")
async def analyze(request: Request, req: SymptomRequest, db: AsyncSession = Depends(get_db)):
    if not req.symptoms.strip():
        raise HTTPException(status_code=400, detail="Symptoms cannot be empty.")
    
    encrypted_symptoms = encrypt_data(req.symptoms)
    client_ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()
    
    result = classifier.predict(req.symptoms)

    if result:
        top_prediction = result[0] 
        
        new_record = ClinicalRecord(
            encrypted_symptoms=encrypted_symptoms,
            predicted_disease=top_prediction["disease"],
            confidence_score=top_prediction["similarity_score"] * 100,
            client_ip=client_ip
        )
        db.add(new_record)
        await db.commit() 
        logger.info(f"Clinical record securely saved to PostgreSQL for disease: {top_prediction['disease']}")

    logger.success(f"Analysis successfully completed for IP: {client_ip}")
    return {"results": result}

@router.get("/api/symptoms")
@limiter.limit("15/minute")
async def get_symptom_list(request: Request):
    return {"symptoms": classifier.get_all_symptoms()}