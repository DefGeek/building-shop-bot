# app/presentation/routers/auth.py
from fastapi import APIRouter, Header, HTTPException, Depends

# ✅ Роутер знает ТОЛЬКО про Application (и про DI-функцию)
from app.application.auth.commands.authenticate_user import (
    AuthenticateUserCommand,
    AuthenticateUserHandler
)
from app.presentation.dependencies import get_auth_handler

router = APIRouter()

@router.post("/telegram")
async def auth_telegram():
    # Временная заглушка, чтобы сервер успешно стартовал
    return {"status": "auth endpoint is ready"}

@router.post("/auth/telegram")
async def auth_telegram(
    x_telegram_init_data: str = Header(alias="X-Telegram-Init-Data"),
    # ✅ Мы запрашиваем готовый хендлер. Роутер НЕ ЗНАЕТ, что внутри него SQLAlchemy или HMAC.
    handler: AuthenticateUserHandler = Depends(get_auth_handler)
):
    try:
        # 1. Presentation преобразует сырой HTTP-запрос в Команду
        command = AuthenticateUserCommand(init_data=x_telegram_init_data)

        # 2. Presentation передает управление в Application
        response = await handler.execute(command)

        # 3. Presentation возвращает ответ клиенту
        return response

    except ValueError as e:
        # Ловим бизнес-ошибки (например, "Invalid Telegram signature")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        # Ловим непредвиденные ошибки
        raise HTTPException(status_code=500, detail="Internal server error")