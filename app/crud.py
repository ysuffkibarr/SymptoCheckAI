from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import domain, schemas
from app.models.domain import BlockedIP

async def create_epidemic_log_async(db: AsyncSession, log: schemas.EpidemicLogCreate):
    db_log = domain.EpidemicLog(
        country=log.country,
        city=log.city,
        district=log.district,
        raw_symptoms=log.raw_symptoms,
        diagnosed_disease=log.diagnosed_disease,
        confidence_score=log.confidence_score
    )
    db.add(db_log)
    return db_log

async def get_recent_epidemic_logs_async(db: AsyncSession, limit: int = 1000):
    query = select(domain.EpidemicLog).order_by(domain.EpidemicLog.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

from sqlalchemy.future import select
from app.models.domain import BlockedIP

async def block_ip_async(db: AsyncSession, ip_address: str, reason: str = None):
    is_blocked = await is_ip_blocked_async(db, ip_address)
    if is_blocked:
        return
        
    new_block = BlockedIP(ip_address=ip_address, reason=reason)
    db.add(new_block)
    try:
        await db.commit()
        await db.refresh(new_block)
        return new_block
    except Exception:
        await db.rollback()

async def is_ip_blocked_async(db: AsyncSession, ip_address: str) -> bool:
    stmt = select(BlockedIP).filter(BlockedIP.ip_address == ip_address)
    result = await db.execute(stmt)
    return result.scalars().first() is not None

async def get_all_blocked_ips_async(db: AsyncSession):
    stmt = select(BlockedIP.ip_address)
    result = await db.execute(stmt)
    return result.scalars().all()