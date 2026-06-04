import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import settings

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Главное меню
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Открыть магазин", web_app={"url": "https://your-mini-app-url.com"})],
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


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())