from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain.order.ports.order_repository import OrderRepository
from app.domain.order.entities.order import Order
from app.domain.order.entities.order_item import OrderItem
from app.domain.user.value_objects.telegram_id import TelegramID
from app.infrastructure.database.models.order_model import OrderModel, OrderItemModel


class OrderRepositoryImpl(OrderRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_domain(self, db_model: OrderModel) -> Order:
        """Преобразует модель БД в доменную сущность"""
        order = Order(
            id=db_model.id,
            telegram_id=TelegramID(db_model.telegram_id),
            total_price=db_model.total_price,
            customer_name=db_model.customer_name,
            phone=db_model.phone,
            address=db_model.address,
            comment=db_model.comment,
            status=db_model.status,
            payment_method=db_model.payment_method,
            created_at=db_model.created_at,
        )
        order.items = [
            OrderItem(
                id=item.id,
                order_id=item.order_id,
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                price=item.price,
            )
            for item in db_model.items
        ]
        return order

    def _to_db_model(self, domain_order: Order) -> OrderModel:
        """Преобразует доменную сущность в модель БД"""
        order_model = OrderModel(
            id=domain_order.id,
            telegram_id=domain_order.telegram_id.value,
            total_price=domain_order.total_price,
            customer_name=domain_order.customer_name,
            phone=domain_order.phone,
            address=domain_order.address,
            comment=domain_order.comment,
            status=domain_order.status,
            payment_method=domain_order.payment_method,
            created_at=domain_order.created_at,
        )
        return order_model

    async def find_by_telegram_id(self, telegram_id: TelegramID) -> List[Order]:
        """Найти все заказы пользователя по telegram_id"""
        result = await self.db.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.telegram_id == telegram_id.value)
            .order_by(OrderModel.created_at.desc())
        )
        db_orders = result.scalars().all()
        return [self._to_domain(order) for order in db_orders]

    async def find_by_id(self, order_id: int) -> Optional[Order]:
        """Найти заказ по ID"""
        result = await self.db.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.id == order_id)
        )
        db_order = result.scalar_one_or_none()
        return self._to_domain(db_order) if db_order else None

    async def create(self, order: Order) -> Order:
        """Создать новый заказ"""
        db_model = self._to_db_model(order)
        self.db.add(db_model)
        await self.db.commit()
        await self.db.refresh(db_model)
        return self._to_domain(db_model)

    async def save(self, order: Order) -> Order:
        """Сохранить заказ (update или insert)"""
        db_model = self._to_db_model(order)
        merged_model = await self.db.merge(db_model)
        await self.db.commit()

        # Явно загружаем items через selectinload, чтобы избежать lazy loading
        result = await self.db.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.id == merged_model.id)
        )
        loaded_model = result.scalar_one()

        return self._to_domain(loaded_model)