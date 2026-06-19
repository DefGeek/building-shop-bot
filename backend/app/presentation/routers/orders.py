from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.database import get_db
from app.presentation.dependencies import get_current_telegram_id
from app.presentation.schemas.order import OrderCreate, OrderResponse
from app.infrastructure.database.models.order_model import OrderModel, OrderItemModel
from app.infrastructure.database.models.product_model import ProductModel
from app.config import settings
from app.application.orders.commands.pay_order import PayOrderFromWalletHandler, PayOrderCommand
from app.infrastructure.repositories.wallet_repository_impl import WalletRepositoryImpl
from app.infrastructure.repositories.transaction_repository_impl import TransactionRepositoryImpl
from app.infrastructure.repositories.order_repository_impl import OrderRepositoryImpl

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/{order_id}/pay")
async def pay_order(
    order_id: int,
    telegram_id: int = Depends(get_current_telegram_id),
    db: AsyncSession = Depends(get_db),
):
    print(f"🔍 PAY ORDER - telegram_id: {telegram_id}, order_id: {order_id}")
    """Оплата заказа с кошелька"""
    wallet_repo = WalletRepositoryImpl(db)
    transaction_repo = TransactionRepositoryImpl(db)
    order_repo = OrderRepositoryImpl(db)

    handler = PayOrderFromWalletHandler(wallet_repo, transaction_repo, order_repo)
    result = await handler.execute(PayOrderCommand(order_id=order_id, telegram_id=telegram_id))

    return {
        "success": result.success,
        "message": result.message,
        "new_balance": result.new_balance
    }


@router.post("/")
async def create_order(
        order_data: OrderCreate,
        telegram_id: int = Depends(get_current_telegram_id),
        db: AsyncSession = Depends(get_db)
):
    print(f"\n🔍 CREATE ORDER - START")
    print(f"🔍 CREATE ORDER - telegram_id: {telegram_id}")
    print(f"🔍 CREATE ORDER - order_data: {order_data}")
    print(f"🔍 CREATE ORDER - items: {order_data.items}")

    try:
        # 1. Проверяем товары и считаем реальную сумму
        total_price = 0.0
        order_items_to_create = []
        items_for_notification = []

        for item in order_data.items:
            print(f"🔍 Processing item: {item}")
            product = await db.get(ProductModel, item.product_id)
            if not product or not product.is_available:
                raise HTTPException(status_code=400, detail=f"Товар с ID {item.product_id} недоступен")

            total_price += product.price * item.quantity
            order_items_to_create.append(OrderItemModel(
                product_id=product.id,
                product_name=product.name,
                quantity=item.quantity,
                price=product.price
            ))
            items_for_notification.append(
                f"• {product.name} x{item.quantity} ({product.price * item.quantity} ₽)"
            )

        # 2. Создаем заказ
        new_order = OrderModel(
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

        # 3. Отправляем уведомление
        order_id = new_order.id
        items_text = "\n".join(items_for_notification)

        try:
            admin_chat_id = getattr(settings, 'ADMIN_CHAT_ID', None)
            if admin_chat_id:
                message = (
                    f"🔔 *Новый заказ #{order_id}!*\n\n"
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

        print(f"✅ ORDER CREATED - order_id: {order_id}")
        return {"order_id": order_id, "status": "created"}

    except Exception as e:
        print(f"❌ CREATE ORDER ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise