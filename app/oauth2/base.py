from collections import namedtuple
from flask_restplus import Namespace
from typing import Tuple


TokenResponse = namedtuple('TokenResponse', ['access_token', 'refresh_token', 'expires_in'])


class BaseOAuth2:
    @classmethod
    def get_code_url(cls, redirect_uri: str) -> str:
        raise NotImplementedError

    @classmethod
    def get_access_token(cls, api: Namespace, code: str, redirect_uri: str) -> Tuple[TokenResponse, dict]:
        raise NotImplementedError

    @classmethod
    def get_refresh_token(cls, api: Namespace, refresh_token: str) -> Tuple[TokenResponse, dict]:
        raise NotImplementedError

    @classmethod
    def get_info(cls, access_token: str) -> dict:
        raise NotImplementedError

    @classmethod
    def get_id_from_info(cls, info: dict) -> str:
        raise NotImplementedError

    @classmethod
    def transform_info(cls, info: dict) -> dict:
        raise NotImplementedError

    @classmethod
    def validate_token(cls, api: Namespace, access_token: str) -> dict:
        raise NotImplementedError

    @classmethod
    def get_user_by_id(cls, api: Namespace, login_id: str) -> dict:
        raise NotImplementedError
