from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from app.database import engine, async_session_maker, Base
from app.infrastructure.database.models.product_model import ProductModel
from app.infrastructure.database.models.order_model import Order, OrderItem
from app.infrastructure.database.models.user_model import UserModel
from app.presentation.routers import auth, products, orders

app = FastAPI(title="СтройМаркет AI API")

# CORS надо чтобы один сайт не мог сделать запрос к другому от себя
# (к примеру, сходить на сайт банка используя cookie и украсть деньги
# (CORS такой ход заблокирует)
app.add_middleware(
    CORSMiddleware,
    # Источники от которых можем принимать информацию
    allow_origins=["https://tubby-unit-reclining.ngrok-free.dev"],
    # в cookie хранится jwt токен, с этим параметром браузер отправит его бэкенду и получит
    # ответ, иначе 401 Unauthorized
    allow_credentials=True,
    # Методы,которые разрешено принимать от браузера
    allow_methods=["GET","POST"],
    # Указываем,какие HTTP заголовки могут приходить от браузера
    allow_headers=["Content-Type", "Authorization", "X-Telegram-Init-Data"],
)

# Роутеры ПОСЛЕ middleware
app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"status": "ok", "message": "СтройМаркет AI API работает"}


# app.on_event декоратор который говорит FastAPI выполнится до того как сервер будет принимать http запросы
@app.on_event("startup")
async def startup_event():
    async with async_session_maker() as db:
        result = await db.execute(select(ProductModel))
        if not result.scalars().first():
            test_products = [
                ProductModel(
                    name="Цемент М500",
                    description="Мешок 50 кг, высокая прочность",
                    price=450.0,
                    image_url="https://avatars.mds.yandex.net/get-mpic/20337182/2a0000019d530e4623cc2b76599fa19038a5/9hq"
                ),
                ProductModel(
                    name="Кирпич красный облицовочный",
                    description="Облицовочный, 1 шт",
                    price=25.5,
                    image_url="https://avatars.mds.yandex.net/i?id=6691a872ec7ccd46c42f39010a8908fa34317850-5843150-images-thumbs&n=13"
                ),
                ProductModel(
                    name="Шпаклевка финишная",
                    description="Ведро 10 кг, белая",
                    price=890.0,
                    image_url="https://avatars.mds.yandex.net/get-mpic/15380440/2a00000199316fbecdc9e3ffa86cada3705c/orig"
                ),
                ProductModel(
                    name="Перфоратор Makita",
                    description="Мощный, 800 Вт, кейс в комплекте",
                    price=12500.0,
                    image_url="https://avatars.mds.yandex.net/i?id=8feae67fb942fd031f3c8b08b49637df_l-5222192-images-thumbs&n=13"
                ),
            ]
            db.add_all(test_products)
            await db.commit()