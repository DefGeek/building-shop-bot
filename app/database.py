# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

# 1. Создаем асинхронный движок
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Поставьте True, чтобы видеть SQL-запросы в консоли при отладке
    pool_pre_ping=True, # Проверяет "живость" соединения (важно для продакшена)
)

# 2. Фабрика асинхронных сессий
# expire_on_commit=False КРИТИЧЕСКИ важен для асинхронной SQLAlchemy!
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 3. Dependency для FastAPI
async def get_db() -> AsyncSession:
    """
    Предоставляет сессию БД для каждого HTTP-запроса.
    Гарантирует закрытие сессии после завершения запроса (даже при ошибке).
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()