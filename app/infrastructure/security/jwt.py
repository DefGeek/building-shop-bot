"""
Каждый раз использовать init_data небезопасно и неэффективно
init_data <- там много данных о юзере и данные о чате, там сложный алгоритм подсчёта и сравнения
jwt_token <- там только информация о допустимости/недопустимости входа для юзера, легко делается и проверяется
"""

import jwt
from datetime import datetime, timedelta
from uuid import UUID
from app.config import settings
from app.domain.user.ports.token_generator import TokenGenerator

class JwtTokenGenerator(TokenGenerator):
    def generate(self, user_id: UUID) -> str:
        expire = datetime.utcnow() + timedelta(days=30)
        payload = {"sub": str(user_id), "exp": expire}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")