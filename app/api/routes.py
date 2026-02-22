from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
import os
from app.limiter import limiter
from app.models.schemas import SymptomRequest
from app.services.ml_service import SymptomClassifier
from app.logger import logger

router = APIRouter()
csv_path = os.path.join("data", "DiseaseAndSymptoms.csv")
classifier = SymptomClassifier(csv_path)

@router.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@router.post("/api/analyze")
@limiter.limit("5/minute")
async def analyze(request: Request, req: SymptomRequest):
    if not req.symptoms.strip():
        logger.warning(f"IP: {request.client.host} tried to send empty symptoms.")
        raise HTTPException(status_code=400, detail="Symptoms cannot be empty.")
    
    logger.info(f"Analysis requested for symptoms: {req.symptoms}")
    
    result = classifier.predict(req.symptoms)
    
    logger.success(f"Successfully predicted for IP: {request.client.host}")
    
    return {"results": result}

@router.get("/api/symptoms")
@limiter.limit("15/minute")
async def get_symptom_list(request: Request):
    return {"symptoms": classifier.get_all_symptoms()}