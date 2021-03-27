from enum import Enum


class EnumUserRole(Enum):
    ADMIN = 1
    USER = 2


class EnumLoginService(Enum):
    GOOGLE = 1
    VK = 2


class EnumRequestStatus(Enum):
    APPLIED = 1
    BOOKED = 2
    CANCELED = 3
    COMPLETED = 4
    DELAYED = 5
    DENIED = 6
    LENT = 7
