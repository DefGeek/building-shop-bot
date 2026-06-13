from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base  # ← ДОБАВЬ ЭТО
from app.config import settings

# 0. Базовый класс для всех моделей (ОБЯЗАТЕЛЬНО!)
Base = declarative_base()

# 1. Создаем асинхронный движок
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# 2. Фабрика асинхронных сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 3. Dependency для FastAPI
async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()