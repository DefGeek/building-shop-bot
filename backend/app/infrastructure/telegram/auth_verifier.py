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
        """
        1)Telegram WebApp берёт user, auth_date и другие данные, формирует из них строку вида auth_date=1234567890\nuser={"id":...}
        (сортирует ключи по алфавиту), вычисляет HMAC-SHA256 от этой строки с секретным ключом
         (который сам является HMAC от токена бота с префиксом "WebAppData"), и добавляет hash=... в init_data.
        2)Браузер получает всю строку init_data (включая hash) и передаёт её на
         бэкенд через заголовок X-Telegram-Init-Data.
        3)FastAPI получает init_data, извлекает hash, формирует такую же строку из остальных данных (сортируя ключи),
         вычисляет HMAC тем же алгоритмом и сравнивает с полученным хешем через hmac.compare_digest
        (безопасное сравнение, защищённое от timing attacks).
        4)Дополнительно проверяется auth_date — данные не должны быть старше 24 часов.
        :param init_data:
        :return:
        """
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