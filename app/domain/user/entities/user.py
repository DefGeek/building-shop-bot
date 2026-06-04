from datetime import datetime
from typing import Optional
from uuid import uuid4, UUID

from domain.user.value_objects.telegram_id import TelegramID
from domain.user.value_objects.user_role import UserRole

class User:
    def __init__(
        self,
        telegram_id: TelegramID,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ):
        self.id: UUID = uuid4()
        self.telegram_id = telegram_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.role: UserRole = UserRole.BUYER
        self.is_active: bool = True
        self.created_at: datetime = datetime.utcnow()
        self.last_login: Optional[datetime] = None

    def update_last_login(self):
        self.last_login = datetime.utcnow()

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name or ''}".strip()