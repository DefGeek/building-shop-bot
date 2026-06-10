from fastapi import FastAPI
from sqlalchemy import select
from app.database import engine, get_db
from app.infrastructure.database.models.product_model import ProductModel
from app.presentation.routers import auth, products

app = FastAPI(title="СтройМаркет AI API")

# Подключаем роутеры
app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"status": "ok", "message": "СтройМаркет AI API работает"}


@app.on_event("startup")
async def startup_event():
    # Создаем таблицы, если их нет
    async with engine.begin() as conn:
        await conn.run_sync(ProductModel.metadata.create_all)

    # Добавляем тестовые товары, если база пустая
    async with get_db() as db:
        result = await db.execute(select(ProductModel))
        if not result.scalars().first():
            test_products = [
                ProductModel(name="Цемент М500", description="Мешок 50 кг, высокая прочность", price=450.0,
                             image_url="https://via.placeholder.com/150"),
                ProductModel(name="Кирпич красный", description="Облицовочный, 1 шт", price=25.5,
                             image_url="https://via.placeholder.com/150"),
                ProductModel(name="Шпаклевка финишная", description="Ведро 10 кг, белая", price=890.0,
                             image_url="https://via.placeholder.com/150"),
                ProductModel(name="Перфоратор Makita", description="Мощный, 800 Вт, кейс в комплекте", price=12500.0,
                             image_url="https://via.placeholder.com/150"),
            ]
            db.add_all(test_products)
            await db.commit()
            print("✅ Тестовые товары добавлены в базу данных")