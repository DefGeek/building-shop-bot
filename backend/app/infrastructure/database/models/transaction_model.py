from sqlalchemy import Column, BigInteger, Float, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import datetime
import uuid
from app.database import Base
from app.domain.wallet.entities.transaction import TransactionStatus

class TransactionModel(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(SQLEnum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    external_payment_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)