from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.domain import EpidemicLog

async def detect_outbreaks(db: AsyncSession):
    """
    Scans the database for statistical anomalies in symptom reports to detect 
    potential geographical outbreaks using database-level grouping.
    """
    now = datetime.now(timezone.utc)
    three_days_ago = now - timedelta(days=3)
    thirty_days_ago = now - timedelta(days=30)

    baseline_query = select(
        EpidemicLog.city, 
        EpidemicLog.district, 
        EpidemicLog.diagnosed_disease, 
        func.count(EpidemicLog.id).label("count")
    ).where(
        EpidemicLog.created_at >= thirty_days_ago,
        EpidemicLog.created_at < three_days_ago
    ).group_by(EpidemicLog.city, EpidemicLog.district, EpidemicLog.diagnosed_disease)
    
    baseline_result = await db.execute(baseline_query)
    baseline_data = {(r.city, r.district, r.diagnosed_disease): r.count for r in baseline_result.all()}

    recent_query = select(
        EpidemicLog.city, 
        EpidemicLog.district, 
        EpidemicLog.diagnosed_disease, 
        func.count(EpidemicLog.id).label("count")
    ).where(
        EpidemicLog.created_at >= three_days_ago
    ).group_by(EpidemicLog.city, EpidemicLog.district, EpidemicLog.diagnosed_disease)

    recent_result = await db.execute(recent_query)

    outbreaks = []

    for row in recent_result.all():
        city, district, disease, recent_count = row.city, row.district, row.diagnosed_disease, row.count
        baseline_count = baseline_data.get((city, district, disease), 0)

        baseline_daily_avg = baseline_count / 27.0 if baseline_count > 0 else 0.1
        recent_daily_avg = recent_count / 3.0

        if recent_daily_avg > (baseline_daily_avg * 5) and recent_count >= 10:
            outbreaks.append({
                "city": city,
                "district": district,
                "disease": disease,
                "baseline_daily_average": round(baseline_daily_avg, 2),
                "recent_daily_average": round(recent_daily_avg, 2),
                "total_recent_cases": recent_count,
                "risk_level": "CRITICAL_RED",
                "alert_message": f"OUTBREAK DETECTED: {disease} cases have spiked in {city}/{district}!"
            })

    outbreaks.sort(key=lambda x: x["total_recent_cases"], reverse=True)
    
    return outbreaks