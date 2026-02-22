import sys
import os
from loguru import logger

if not os.path.exists("logs"):
    os.makedirs("logs")

logger.remove()

logger.add(
    sys.stdout, 
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

logger.add(
    "logs/symptocheck.log", 
    rotation="1 MB", 
    retention="10 days", 
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}"
)