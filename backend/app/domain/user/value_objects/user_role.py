from enum import Enum

class UserRole(str, Enum):
    BUYER = "buyer"
    MANAGER = "manager"
    ADMIN = "admin"