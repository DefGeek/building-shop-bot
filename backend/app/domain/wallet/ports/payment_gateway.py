from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class PaymentRequest:
    amount: float
    description: str
    external_id: str  # Наш ID транзакции

@dataclass
class PaymentResponse:
    external_payment_id: str
    confirmation_url: str

class PaymentGateway(ABC):
    @abstractmethod
    async def create_payment(self, request: PaymentRequest) -> PaymentResponse:
        pass