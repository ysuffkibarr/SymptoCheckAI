from fastapi import APIRouter, HTTPException, Request, Depends, Header
from fastapi.responses import HTMLResponse
import os
from app.limiter import limiter
from app.models.schemas import SymptomRequest
from app.services.ml_service import SymptomClassifier
from app.logger import logger

router = APIRouter()
csv_path = os.path.join("data", "DiseaseAndSymptoms.csv")
classifier = SymptomClassifier(csv_path)

# 🔒 YENİ: SİBER GÜVENLİK KİLİDİ (RAPIDAPI BYPASS KORUMASI)
def verify_security_key(x_sympto_key: str = Header(None)):
    SECRET_KEY = "kibar-ai-production-2026"
    if x_sympto_key != SECRET_KEY:
        raise HTTPException(
            status_code=401, 
            detail="Unauthorized Bypass Attempt! Please use the official RapidAPI endpoint."
        )

@router.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

# 🔒 KORUMALI ROTA: "dependencies=[Depends(verify_security_key)]" eklendi!
@router.post("/api/analyze", dependencies=[Depends(verify_security_key)])
@limiter.limit("5/minute")
async def analyze(request: Request, req: SymptomRequest):
    if not req.symptoms.strip():
        logger.warning(f"IP: {request.client.host} tried to send empty symptoms.")
        raise HTTPException(status_code=400, detail="Symptoms cannot be empty.")
    
    logger.info(f"Analysis requested for symptoms: {req.symptoms}")
    
    result = classifier.predict(req.symptoms)
    
    logger.success(f"Successfully predicted for IP: {request.client.host}")
    
    return {"results": result}

# Bu rota sadece kelimeleri listelediği için açık kalabilir
@router.get("/api/symptoms")
@limiter.limit("15/minute")
async def get_symptom_list(request: Request):
    return {"symptoms": classifier.get_all_symptoms()}