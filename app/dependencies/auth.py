from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import Type

from .db import get_db
from ..oauth2 import BaseOAuth2, get_service as get_service_, validate_service
from ..models import EnumUserRole, Users


apiKey_scheme = APIKeyHeader(name='authorization',
                             description='The authorization token with service in format service.token',
                             auto_error=False)


def _get_key(key: str = Depends(apiKey_scheme)) -> str:
    if key is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Access token required')
    return key


def get_service(key: str = Depends(_get_key)) -> Type[BaseOAuth2]:
    service_name = key.split('.')[0]
    if not validate_service(service_name):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Invalid service supplied')
    return get_service_(service_name)


def get_access_token(key: str = Depends(_get_key)) -> str:
    service_name = key.split('.')[0]
    return key[len(service_name) + 1:]


def get_current_user(service: Type[BaseOAuth2] = Depends(get_service),
                     access_token: str = Depends(get_access_token),
                     db: Session = Depends(get_db)) -> Users:
    validation_data = service.validate_token(access_token)
    return service.get_user_by_id(service.get_id_from_info(validation_data), db)


def get_admin(user: Users = Depends(get_current_user)) -> Users:
    if not user.role == EnumUserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Admin access required')
    return user
