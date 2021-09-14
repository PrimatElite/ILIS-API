from enum import Enum


class EnumUserRole(str, Enum):
    ADMIN = 'ADMIN'
    USER = 'USER'


class EnumLoginService(str, Enum):
    GOOGLE = 'GOOGLE'
    VK = 'VK'


class EnumRequestStatus(str, Enum):
    APPLIED = 'APPLIED'
    BOOKED = 'BOOKED'
    CANCELED = 'CANCELED'
    COMPLETED = 'COMPLETED'
    DELAYED = 'DELAYED'
    DENIED = 'DENIED'
    LENT = 'LENT'
