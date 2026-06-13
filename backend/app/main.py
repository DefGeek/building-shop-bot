import asyncio
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from app.config import settings
from app.infrastructure.database.models.user_model import Base
from app.database import engine

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Открыть магазин", web_app={"url": "https://tubby-unit-reclining.ngrok-free.dev/"})],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
    ])
    return keyboard


@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "👋 Добро пожаловать в СтройМаркет AI!\n\n"
        "Нажмите кнопку ниже, чтобы открыть магазин:",
        reply_markup=get_main_keyboard()
    )


async def run_web_server():
    """Функция для запуска FastAPI сервера"""
    config = uvicorn.Config("app.web:app", host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Запускаем бота и веб-сервер конкурентно (асинхронно) в одном event loop,
    # чтобы они не блокировали выполнение друг друга.
    await asyncio.gather(
        dp.start_polling(bot),
        run_web_server()
    )


if __name__ == "__main__":
    asyncio.run(main())