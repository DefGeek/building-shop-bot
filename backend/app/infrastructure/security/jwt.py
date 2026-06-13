import jwt
from datetime import datetime, timedelta
from uuid import UUID

from app.config import settings
from app.domain.user.ports.token_generator import TokenGenerator
from app.domain.user.value_objects.telegram_id import TelegramID


class JwtTokenGenerator(TokenGenerator):
    def generate(self, user_id: UUID, telegram_id: TelegramID) -> str:
        expire = datetime.utcnow() + timedelta(days=30)
        payload = {
            "sub": str(user_id),
            "telegram_id": telegram_id.value,  # <-- ДОБАВЛЕНО в payload
            "exp": expire
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")