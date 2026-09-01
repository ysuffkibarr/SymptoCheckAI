from cryptography.fernet import Fernet
import os
from app.logger import logger

ENCRYPTION_KEY = os.getenv("AES_SECRET_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

def encrypt_data(data: str) -> str:
    """Encrypts sensitive health data using AES-256."""
    try:
        return cipher_suite.encrypt(data.encode()).decode()
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise

def decrypt_data(encrypted_data: str) -> str:
    """Decrypts the encrypted data back to plain text."""
    try:
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise