from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config import settings

# Базовый класс для всех моделей
# Далее мы наследуем от него другие классы sqlalchemy что позволяет:
# 1. Названия колонок,их типы,взаимосвязи с др таблицами будут хранитсья в метаданных
# 2. Когда наследуем класс от Base sqlaclhemy будет всегда проверять создана ли данная таблица
Base = declarative_base()

# Создаем асинхронный движок
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False, # отменяем логирование базы в консоль
    pool_pre_ping=True, #проверка соединения на живучесть, если мертво - создаётся новое
)

# Фабрика асинхронных сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession, # просьба к фабрике сессий создавать именно асинхронные сессии
    expire_on_commit=False, # после commit sqlalchemy будет помечать данные как изменённые, что заставит сессию
    #делать запрос заново
)

# Dependency для FastAPI
# асинхронная функция генератор
async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close() # страховка от утечек соединений
            # также это I/O операция и её асинхронное закрытие не двёт блокировать главный поток event loop