from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime

from app.domain.wallet.ports.wallet_repository import WalletRepository
from app.domain.wallet.ports.transaction_repository import TransactionRepository
from app.domain.wallet.entities.transaction import Transaction, TransactionStatus
from app.domain.user.value_objects.telegram_id import TelegramID
from app.infrastructure.repositories.order_repository_impl import OrderRepositoryImpl


@dataclass
class PayOrderCommand:
    order_id: int
    telegram_id: int


@dataclass
class PayOrderResponse:
    success: bool
    message: str
    new_balance: float | None = None


class PayOrderFromWalletHandler:
    def __init__(
        self,
        wallet_repo: WalletRepository,
        transaction_repo: TransactionRepository,
        order_repo: OrderRepositoryImpl
    ):
        self.wallet_repo = wallet_repo
        self.transaction_repo = transaction_repo
        self.order_repo = order_repo

    async def execute(self, command: PayOrderCommand) -> PayOrderResponse:
        telegram_id = TelegramID(command.telegram_id)
        print(f"\n💰 PAY START - order_id: {command.order_id}, telegram_id: {command.telegram_id}")

        # 1. Находим заказ
        order = await self.order_repo.find_by_id(command.order_id)
        if not order:
            raise ValueError("Заказ не найден")

        if order.telegram_id.value != command.telegram_id:
            raise ValueError("Заказ не принадлежит пользователю")

        if order.status != "new":
            raise ValueError("Заказ уже оплачен или отменен")

        # 2. Находим кошелек
        wallet = await self.wallet_repo.find_by_telegram_id(telegram_id)
        if not wallet:
            raise ValueError("Кошелек не найден")

        print(f"💰 PAY - balance before: {wallet.balance}, order total: {order.total_price}")

        # 3. Проверяем баланс
        if wallet.balance < order.total_price:
            raise ValueError("Недостаточно средств на балансе")

        # 4. Списываем средства
        wallet.withdraw(order.total_price)
        print(f"💰 PAY - balance after withdraw: {wallet.balance}")

        await self.wallet_repo.save(wallet)
        print(f"💰 PAY - balance after save: {wallet.balance}")

        # 5. Создаем транзакцию
        transaction = Transaction(
            id=uuid4(),
            telegram_id=telegram_id,
            amount=order.total_price,
            status=TransactionStatus.SUCCESS,
            external_payment_id=f"order_{order.id}",
            created_at=datetime.utcnow()
        )
        await self.transaction_repo.create(transaction)

        # 6. Обновляем статус заказа
        order.status = "paid"
        order.payment_method = "wallet"
        await self.order_repo.save(order)

        print(f"💰 PAY DONE - final balance: {wallet.balance}")

        return PayOrderResponse(
            success=True,
            message="Заказ успешно оплачен с кошелька",
            new_balance=wallet.balance
        )