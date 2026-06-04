# infrastructure/telegram/auth_verifier.py
import hashlib
import hmac
from urllib.parse import parse_qsl
from datetime import datetime

from app.config import settings
from domain.user.repositories.auth_verifier import AuthVerifier # <-- Импортируем интерфейс

class TelegramAuthVerifier(AuthVerifier): # <-- Наследуемся от него
    def verify(self, init_data: str) -> dict:
        data = dict(parse_qsl(init_data))
        hash_value = data.pop('hash')

        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()))

        secret = hmac.new(b"WebAppData", settings.TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(calculated_hash, hash_value):
            raise ValueError("Invalid Telegram signature")

        if (datetime.utcnow().timestamp() - int(data.get('auth_date', 0))) > 86400:
            raise ValueError("Telegram data expired")

        return data