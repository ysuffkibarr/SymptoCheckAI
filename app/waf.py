from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.logger import logger

BANNED_IPS = set()

TRAP_ROUTES = ["/wp-admin", "/.env", "/api/hidden_admin", "/config.json", "/phpmyadmin"]

class HoneyMindWAFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()

        if client_ip in BANNED_IPS:
            logger.warning(f"[HoneyMind WAF] Request blocked from banned IP -> {client_ip}")
            return JSONResponse(status_code=403, content={"detail": "Access Denied by HoneyMind WAF. Your IP is banned."})

        if any(trap in request.url.path for trap in TRAP_ROUTES):
            BANNED_IPS.add(client_ip)
            logger.critical(f"[HoneyMind WAF] TRAP TRIGGERED! Malicious IP Blacklisted: {client_ip} | Attempted path: {request.url.path}")
            return JSONResponse(status_code=403, content={"detail": "Malicious activity detected. IP permanently banned."})

        user_agent = request.headers.get("user-agent", "").lower()
        malicious_agents = ["sqlmap", "nmap", "dirbuster", "nikto", "zgrab"]
        
        if any(bot in user_agent for bot in malicious_agents):
            BANNED_IPS.add(client_ip)
            logger.critical(f"[HoneyMind WAF] Malicious tool detected! IP: {client_ip} | Tool: {user_agent}")
            return JSONResponse(status_code=403, content={"detail": "Automated attack tools are strictly prohibited."})

        response = await call_next(request)
        return response