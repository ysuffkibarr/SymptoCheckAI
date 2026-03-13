from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
from pathlib import Path
from typing import List
import httpx
import asyncio

from app.limiter import limiter
from app.models.schemas import SymptomRequest
from app.models import schemas
from app.services.ml_service import SymptomClassifier
from app.logger import logger
from app.security import encrypt_data
from app.database import get_db
from app.models.domain import ClinicalRecord 
from app import crud
from app.services.epidemic_service import detect_outbreaks
from app.utils import get_client_ip

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
csv_path = BASE_DIR / "data" / "DiseaseAndSymptoms.csv"
model_path = BASE_DIR / "data" / "semantic_cache.pkl"
index_path = BASE_DIR / "static" / "index.html"

classifier = SymptomClassifier(str(csv_path), str(model_path))

async def get_anonymized_location(ip_address: str):
    """
    Takes an IP address, queries a fast geolocation API, and returns 
    ONLY the city and country. The IP is then discarded for GDPR/KVKK compliance.
    """
    if ip_address in ["127.0.0.1", "::1", "localhost"]:
        return {"country": "Turkey", "city": "Test City", "district": "Localhost"}
        
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"https://ipwho.is/{ip_address}")
            data = response.json()
            
            if data.get("success"):
                return {
                    "country": data.get("country", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "district": data.get("region", "Unknown")
                }
    except Exception as e:
        logger.warning(f"Geolocation failed for IP {ip_address}: {str(e)}")
        
    return {"country": "Unknown", "city": "Unknown", "district": "Unknown"}

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
    client_ip = get_client_ip(request)

    result = await asyncio.to_thread(classifier.predict, req.symptoms)

    if result:
        top_prediction = result[0] 
        confidence = top_prediction["similarity_score"] * 100
        disease_name = top_prediction["disease"]

        location_data = await get_anonymized_location(client_ip)

        new_record = ClinicalRecord(
            encrypted_symptoms=encrypted_symptoms,
            predicted_disease=disease_name,
            confidence_score=confidence,
            client_ip=client_ip
        )
        db.add(new_record)
        
        epidemic_entry = schemas.EpidemicLogCreate(
            country=location_data["country"],
            city=location_data["city"],
            district=location_data["district"],
            raw_symptoms=req.symptoms,
            diagnosed_disease=disease_name,
            confidence_score=round(top_prediction["similarity_score"], 3)
        )
        await crud.create_epidemic_log_async(db=db, log=epidemic_entry)
        
        try:
            await db.commit() 
            logger.info(f"Clinical record securely saved to PostgreSQL for disease: {disease_name}")
            logger.info(f"ANONYMOUS OUTBREAK DATA SENT: {disease_name} spotted in {location_data['city']}")
        except Exception as e:
            await db.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during data saving.")

    logger.success(f"Analysis successfully completed for IP: {client_ip}")
    return {"results": result}

@router.post("/api/epidemic_log", response_model=schemas.EpidemicLogResponse)
async def log_epidemic(log_data: schemas.EpidemicLogCreate, db: AsyncSession = Depends(get_db)):
    """
    In the user's symptom analyses, the results and location are recorded in the data logs.
    """
    try:
        log = await crud.create_epidemic_log_async(db=db, log=log_data)
        await db.commit()
        return log
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create epidemic log.")

@router.get("/api/epidemic/logs", response_model=List[schemas.EpidemicLogResponse])
async def get_epidemic_data(limit: int = 1000, db: AsyncSession = Depends(get_db)):
    """
    The visualization map and AI anomaly detection list recent cases.
    """
    try:
        return await crud.get_recent_epidemic_logs_async(db=db, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching epidemic data: {str(e)}")

@router.get("/api/symptoms")
@limiter.limit("15/minute")
async def get_symptom_list(request: Request):
    return {"symptoms": classifier.get_all_symptoms()}

@router.get("/api/epidemic/outbreaks")
async def check_for_outbreaks(db: AsyncSession = Depends(get_db)):
    """
    Scans the database using statistical anomaly detection to find active outbreaks.
    Returns a list of CRITICAL_RED zones for the heatmap dashboard.
    """
    try:
        active_alerts = await detect_outbreaks(db)
        
        return {
            "status": "success",
            "analyzed_timeframe": "Last 30 days",
            "active_outbreaks": active_alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")