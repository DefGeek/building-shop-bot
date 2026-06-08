from dataclasses import dataclass

@dataclass(frozen=True)
class TelegramID:
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Telegram ID должно быть положительным")