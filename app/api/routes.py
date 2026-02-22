from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import os

from app.models.schemas import SymptomRequest
from app.services.ml_service import SymptomClassifier

router = APIRouter()

csv_path = os.path.join("data", "DiseaseAndSymptoms.csv")
classifier = SymptomClassifier(csv_path)

@router.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@router.post("/api/analyze")
async def analyze(req: SymptomRequest):
    if not req.symptoms.strip():
        raise HTTPException(status_code=400, detail="Symptoms cannot be empty.")
    return {"results": classifier.predict(req.symptoms)}

@router.get("/api/symptoms")
async def get_symptom_list():
    return {"symptoms": classifier.get_all_symptoms()}