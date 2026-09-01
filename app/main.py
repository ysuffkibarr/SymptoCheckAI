from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.api import routes
from app.limiter import limiter
from app.logger import logger 
from app.waf import HoneyMindWAFMiddleware
from app.database import engine, Base 

app = FastAPI(title="SymptoCheckAI API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(HoneyMindWAFMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False, 
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.include_router(routes.router)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    logger.info("SymptoCheckAI Backend Services Successfully Started!")
    logger.info("HoneyMind WAF is ACTIVE.")
    logger.info("Async PostgreSQL Database Engine is ONLINE.")