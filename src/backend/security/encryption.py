import base64
import os
from cryptography.fernet import Fernet

class SecureStorage:
    def __init__(self, key=None):
        if not key:
            key = os.getenv("SECRET_KEY", "CleanGeniusAISecretKey2024SecureKey==")
        # Ensure 32 url-safe base64 key
        key_bytes = key.encode('utf-8')
        key_padded = key_bytes.ljust(32, b'=')[:32]
        self.fernet = Fernet(base64.urlsafe_b64encode(key_padded))

    def encrypt(self, plain_text):
        if not plain_text:
            return ""
        return self.fernet.encrypt(plain_text.encode('utf-8')).decode('utf-8')

    def decrypt(self, cipher_text):
        if not cipher_text:
            return ""
        try:
            return self.fernet.decrypt(cipher_text.encode('utf-8')).decode('utf-8')
        except Exception:
            return ""
