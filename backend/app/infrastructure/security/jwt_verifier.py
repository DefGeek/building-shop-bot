import jwt
from app.config import settings
from app.domain.user.ports.token_verifier import TokenVerifier
from fastapi import HTTPException, status


class JwtTokenVerifier(TokenVerifier):
    def verify(self, token: str) -> int:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            telegram_id = payload.get("telegram_id")

            if telegram_id is None:
                raise ValueError("telegram_id отсутствует в payload")

            return int(telegram_id)

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен просрочен")
        except jwt.InvalidSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверная подпись токена")
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен")