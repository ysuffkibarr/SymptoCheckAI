from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import os
from pathlib import Path
from app.limiter import limiter
from app.models.schemas import SymptomRequest
from app.services.ml_service import SymptomClassifier
from app.logger import logger
from app.security import encrypt_data 

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
csv_path = BASE_DIR / "data" / "DiseaseAndSymptoms.csv"
model_path = BASE_DIR / "data" / "model_cache.pkl"
index_path = BASE_DIR / "static" / "index.html"

classifier = SymptomClassifier(str(csv_path), str(model_path))

@router.get("/", response_class=HTMLResponse)
async def root():
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@router.post("/api/analyze")
@limiter.limit("5/minute")
async def analyze(request: Request, req: SymptomRequest):
    if not req.symptoms.strip():
        logger.warning(f"IP: {request.client.host} tried to send empty symptoms.")
        raise HTTPException(status_code=400, detail="Symptoms cannot be empty.")

    encrypted_symptoms = encrypt_data(req.symptoms)
    logger.info(f"Analysis Requested. Encrypted Payload (Data for DB): {encrypted_symptoms}")
    
    result = classifier.predict(req.symptoms)
    logger.success(f"Successfully predicted for IP: {request.client.host}")
    
    return {"results": result}

@router.get("/api/symptoms")
@limiter.limit("15/minute")
async def get_symptom_list(request: Request):
    return {"symptoms": classifier.get_all_symptoms()}