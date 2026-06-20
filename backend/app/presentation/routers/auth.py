"""
auth.py получает сырой HTTP-запрос.
dependencies.py собирает конкретные реализации из infrastructure (сессию БД, верификатор).
Эти реализации "засовываются" внутрь объекта application (Handler).
Handler выполняет конкретное бизнес-поведение, вообще не зная, как и откуда взялись эти зависимости.
"""
from fastapi import APIRouter, Header, HTTPException, Depends

from app.application.auth.commands.authenticate_user import (
    AuthenticateUserCommand,
    AuthenticateUserHandler
)
from app.presentation.dependencies import get_auth_handler

router = APIRouter()


@router.post("/auth/telegram")
async def auth_telegram(
        x_telegram_init_data: str = Header(alias="X-Telegram-Init-Data"),
        handler: AuthenticateUserHandler = Depends(get_auth_handler)
):
    try:
        command = AuthenticateUserCommand(init_data=x_telegram_init_data)
        response = await handler.execute(command)
        return response

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        print(f"❌ DEBUG: Исключение: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")