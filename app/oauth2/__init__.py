from .base import BaseOAuth2
from .google import GoogleOAuth2
from .vk import VKOAuth2

from ..models.enums import EnumLoginService

from typing import Type


def get_service(service: str) -> Type[BaseOAuth2]:
    service_map = {
        EnumLoginService.GOOGLE.name: GoogleOAuth2,
        EnumLoginService.VK.name: VKOAuth2
    }
    return service_map[service]


def validate_service(service: str) -> bool:
    return service in EnumLoginService.__members__
