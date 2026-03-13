import sys
import os
import asyncio
import random
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import domain
from app.database import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete

AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(domain.Base.metadata.create_all)

async def seed_data():
    await setup_database()
    print("🌱 Tables verified. Starting synthetic data seeding...")
    
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(delete(domain.EpidemicLog))
            await db.commit()
            print("🧹 Old data cleared.")

            cities = ["Istanbul", "Ankara", "Izmir", "Antalya", "Adana"]
            generic_diseases = [
                ("Common Cold", "runny nose, slight cough, sneezing"),
                ("Allergy", "itchy eyes, sneezing, skin rash"),
                ("Headache", "mild head pain, stress"),
                ("Gastritis", "stomach ache, nausea")
            ]

            logs = []

            now = datetime.now(timezone.utc).replace(tzinfo=None)

            print("📊 Generating normal health data (Baseline)...")
            for _ in range(1000):
                days_ago = random.randint(0, 30)
                disease, symptoms = random.choice(generic_diseases)
                
                log = domain.EpidemicLog(
                    country="Turkey",
                    city=random.choice(cities),
                    district="Merkez",
                    raw_symptoms=symptoms,
                    diagnosed_disease=disease,
                    confidence_score=round(random.uniform(0.60, 0.95), 3),
                    created_at=now - timedelta(days=days_ago, hours=random.randint(0, 23))
                )
                logs.append(log)

            print("🚨 ATTENTION: Injecting Respiratory Outbreak into Bursa/Gürsu!")
            outbreak_disease = "Viral Pneumonia"
            outbreak_symptoms = ["high fever, severe cough, shortness of breath", "chest pain, fever, fatigue", "can't breathe, burning chest, sweating"]

            for _ in range(300):
                days_ago = random.randint(0, 3) 
                
                log = domain.EpidemicLog(
                    country="Turkey",
                    city="Bursa",
                    district="Gürsu",
                    raw_symptoms=random.choice(outbreak_symptoms),
                    diagnosed_disease=outbreak_disease,
                    confidence_score=round(random.uniform(0.80, 0.99), 3),
                    created_at=now - timedelta(days=days_ago, hours=random.randint(0, 23))
                )
                logs.append(log)

            db.add_all(logs)
            await db.commit()
            print(f"✅ Success! A total of {len(logs)} cases injected into the database.")

        except Exception as e:
            print(f"❌ An error occurred: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(seed_data())