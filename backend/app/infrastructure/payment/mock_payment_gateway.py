import uuid
from app.domain.wallet.ports.payment_gateway import PaymentGateway, PaymentRequest, PaymentResponse


class MockPaymentGateway(PaymentGateway):
    async def create_payment(self, request: PaymentRequest) -> PaymentResponse:
        # Генерируем фейковый ID платежа, как это делает ЮKassa
        external_payment_id = f"mock_pay_{uuid.uuid4().hex[:8]}"

        # Возвращаем фейковую ссылку на оплату
        # В реальности тут была бы ссылка на форму ЮKassa
        confirmation_url = f"https://mock-yookassa.test/pay/{external_payment_id}?amount={request.amount}"

        return PaymentResponse(
            external_payment_id=external_payment_id,
            confirmation_url=confirmation_url
        )