from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.database import get_db
from app.presentation.dependencies import get_current_telegram_id
from app.presentation.schemas.order import OrderCreate, OrderResponse
from app.infrastructure.database.models.order_model import Order, OrderItem
from app.infrastructure.database.models.product_model import ProductModel
from app.config import settings

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    telegram_id: int = Depends(get_current_telegram_id),
    db: AsyncSession = Depends(get_db)
):
    # 1. Проверяем товары и считаем реальную сумму (защита от подделки цены на фронтенде)
    total_price = 0.0
    order_items_to_create = []
    
    for item in order_data.items:
        product = await db.get(ProductModel, item.product_id)
        if not product or not product.is_available:
            raise HTTPException(status_code=400, detail=f"Товар с ID {item.product_id} недоступен")
        
        total_price += product.price * item.quantity
        order_items_to_create.append(OrderItem(
            product_id=product.id,
            product_name=product.name,
            quantity=item.quantity,
            price=product.price
        ))

    # 2. Создаем заказ
    new_order = Order(
        telegram_id=telegram_id,
        total_price=total_price,
        customer_name=order_data.customer_name,
        phone=order_data.phone,
        address=order_data.address,
        comment=order_data.comment,
        items=order_items_to_create
    )
    
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)

    # 3. Отправляем уведомление админу в Telegram
    try:
        admin_chat_id = getattr(settings, 'ADMIN_CHAT_ID', None)
        if admin_chat_id:
            items_text = "\n".join([f"• {item.product_name} x{item.quantity} ({item.price * item.quantity} ₽)" for item in order_items_to_create])
            message = (
                f"🔔 *Новый заказ #{new_order.id}!*\n\n"
                f"👤 *Клиент:* {order_data.customer_name}\n"
                f"📞 *Телефон:* {order_data.phone}\n"
                f"🏠 *Адрес:* {order_data.address}\n"
                f"💬 *Комментарий:* {order_data.comment or 'Нет'}\n\n"
                f"🛒 *Товары:*\n{items_text}\n\n"
                f"💰 *Итого:* {total_price} ₽"
            )
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={"chat_id": admin_chat_id, "text": message, "parse_mode": "Markdown"}
                )
    except Exception as e:
        print(f"Ошибка отправки уведомления в Telegram: {e}")

    return new_order
