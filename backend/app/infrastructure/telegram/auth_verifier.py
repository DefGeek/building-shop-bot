import hashlib
import hmac
import json
from urllib.parse import parse_qsl
from datetime import datetime
from typing import Dict, Any

from app.config import settings
from app.domain.user.ports.auth_verifier import AuthVerifier


class TelegramAuthVerifier(AuthVerifier):
    def verify(self, init_data: str) -> Dict[str, Any]:
        # 1. Парсим строку запроса в словарь
        data = dict(parse_qsl(init_data))

        # 2. Извлекаем хэш для проверки
        hash_value = data.pop('hash', '')

        # 3. Формируем строку для проверки подписи (до изменения данных!)
        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()))

        # 4. Генерируем секретный ключ
        secret = hmac.new(b"WebAppData", settings.TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()

        # 5. Вычисляем ожидаемый хэш
        calculated_hash = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()

        # 6. Сравниваем хэши
        if not hmac.compare_digest(calculated_hash, hash_value):
            raise ValueError("Invalid Telegram signature")

        # 7. Проверяем срок действия
        if (datetime.utcnow().timestamp() - int(data.get('auth_date', 0))) > 86400:
            raise ValueError("Telegram data expired")

        # 8. === КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ ===
        # Парсим JSON из поля 'user' и добавляем его в словарь
        if 'user' in data:
            try:
                user_data = json.loads(data['user'])
                data['user'] = user_data
            except json.JSONDecodeError:
                raise ValueError("Invalid user data format")

        return data