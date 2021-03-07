from enum import Enum


class EnumUserRole(Enum):
    ADMIN = 1
    USER = 2


class EnumLoginService(Enum):
    GOOGLE = 1
    VK = 2
