import hashlib
import hmac
from urllib.parse import parse_qsl
from datetime import datetime
from typing import Dict, Any

from app.config import settings
from app.domain.user.ports.auth_verifier import AuthVerifier


class TelegramAuthVerifier(AuthVerifier):
    def verify(self, init_data: str) -> Dict[str, Any]:
        """
        # т.е. серверы telegram берут данные юзера (id и тд) и токен бота и делают по ним хеш
        # и отпрпавляют на фронтенд, злоумышленник видит ДАННЫЕ+ХЕШ ОТ СЕРВЕРОВв
        # Злоумышленник может поменять данные,но не видит токен бота и поэтому
        # хеш посчитать правильно он не может и отрпавляет на бэкенд
        # бэкенд достаёт из базы данные,берёт токен и еслии на фронте
        # злоумышленние ничего не менял, то это действительно тот юзер который
        # за себя выдаёт
        """
        # 1. Парсим строку запроса в словарь
        # parse_qsl функция Python модуля urllib.parse, которая разбирает
        # строку URL-параметров (где ключи и значения разделены через & и =)
        # и правращает её в список картежей
        data = dict(parse_qsl(init_data))

        # 2. Извлекаем хэш и удаляем его из данных для дальнейшей проверки
        hash_value = data.pop('hash', '')

        # 3. Сортируем оставшиеся ключи по алфавиту и соединяем их через перенос строки
        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()))

        # 4. Генерируем секретный ключ на основе токена бота и строки "WebAppData"
        secret = hmac.new(b"WebAppData", settings.TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()

        # 5. Вычисляем ожидаемый хэш из отсортированных данных
        calculated_hash = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()

        # 6. Сравниваем хэши (compare_digest защищает от атак по времени выполнения)
        if not hmac.compare_digest(calculated_hash, hash_value):
            raise ValueError("Invalid Telegram signature")

        # 7. Проверяем, что данные не устарели (например, старше 24 часов)
        if (datetime.utcnow().timestamp() - int(data.get('auth_date', 0))) > 86400:
            raise ValueError("Telegram data expired")

        # 8. Возвращаем проверенные данные
        return data