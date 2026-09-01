from slowapi import Limiter
from fastapi import Request
from app.utils import get_client_ip

limiter = Limiter(key_func=get_client_ip)