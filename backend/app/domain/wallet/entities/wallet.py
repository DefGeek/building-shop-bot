from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from app.domain.user.value_objects.telegram_id import TelegramID


@dataclass
class Wallet:
    """Кошелек пользователя"""
    id: UUID
    telegram_id: TelegramID
    balance: float
    created_at: datetime
    updated_at: datetime

    def deposit(self, amount: float) -> None:
        """Пополнение баланса"""
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self.balance += amount
        self.updated_at = datetime.utcnow()

    def withdraw(self, amount: float) -> None:
        """Списание средств"""
        if amount <= 0:
            raise ValueError("Сумма списания должна быть положительной")
        if self.balance < amount:
            raise ValueError("Недостаточно средств на балансе")
        self.balance -= amount
        self.updated_at = datetime.utcnow()