from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request
import time

from app.database import AsyncSessionLocal
from app.crud import is_ip_blocked_async, block_ip_async
from app.utils import get_client_ip
from app.logger import logger

request_counts = {}
BLOCK_THRESHOLD = 50
TIME_WINDOW = 60

class WAFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = get_client_ip(request)
        current_time = time.time()

        async with AsyncSessionLocal() as db:
            if await is_ip_blocked_async(db, client_ip):
                logger.warning(f"WAF: Blocked IP access attempt - {client_ip}")
                return JSONResponse(status_code=403, content={"detail": "Access Denied: Your IP is permanently blocked."})

            if client_ip not in request_counts:
                request_counts[client_ip] = []

            request_counts[client_ip] = [t for t in request_counts[client_ip] if current_time - t < TIME_WINDOW]
            request_counts[client_ip].append(current_time)

            if len(request_counts[client_ip]) > BLOCK_THRESHOLD:
                await block_ip_async(db, client_ip, reason="Rate limit exceeded (Possible DDoS/Brute Force)")
                logger.error(f"WAF: Suspicious activity detected, IP permanently blocked - {client_ip}")
                return JSONResponse(status_code=403, content={"detail": "Access Denied: Suspicious activity detected."})

        response = await call_next(request)
        return response