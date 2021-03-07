from flask import request
from flask_restplus import Namespace
from functools import wraps
from http import HTTPStatus
from typing import Callable, Tuple, Type, Union

from ..models import Users
from ..models.enums import EnumUserRole
from ..oauth2 import BaseOAuth2, get_service, validate_service


_LOGIN_SERVICE_HEADER = 'login_service'
_ACCESS_TOKEN_HEADER = 'access_token'


def get_token_from_headers() -> Union[Tuple[str, str], None]:
    if 'authorization' not in request.headers:
        return None
    key = request.headers['authorization'].split()[-1]
    if '.' not in key:
        return None
    service = key.split('.')[0]
    access_token = key[len(service) + 1:]
    return access_token, service


def token_required(f: Callable) -> Callable:
    @wraps(f)
    def decorated(*args, **kwargs):
        api = args[0].api
        key = get_token_from_headers()
        if key is None:
            api.abort(HTTPStatus.UNAUTHORIZED, 'Access token required')
        access_token, service = key
        check_service(api, service)
        request.environ[_ACCESS_TOKEN_HEADER] = access_token
        request.environ[_LOGIN_SERVICE_HEADER] = service
        return f(*args, **kwargs)

    return decorated


def get_service_from_request() -> Type[BaseOAuth2]:
    return get_service(request.environ[_LOGIN_SERVICE_HEADER])


def get_token_from_request() -> str:
    return request.environ[_ACCESS_TOKEN_HEADER]


def get_user_from_request(api: Namespace) -> dict:
    service = get_service_from_request()
    validation_data = service.validate_token(api, get_token_from_request())
    return service.get_user_by_id(api, service.get_id_from_info(validation_data))


def check_admin(api: Namespace, user: dict):
    if not user['role'] == EnumUserRole.ADMIN.name:
        api.abort(HTTPStatus.FORBIDDEN, 'Admin access required')


def check_service(api: Namespace, service: str):
    if not validate_service(service):
        api.abort(HTTPStatus.UNAUTHORIZED, 'Invalid service supplied')
