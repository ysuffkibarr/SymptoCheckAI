from slowapi import Limiter
from fastapi import Request

def get_real_ip(request: Request):
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host

limiter = Limiter(key_func=get_real_ip)