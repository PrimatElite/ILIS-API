from collections import namedtuple
from sqlalchemy.orm import Session
from typing import Tuple

from ..models import ORMUsers


TokenResponse = namedtuple('TokenResponse', ['access_token', 'refresh_token', 'expires_in'])


class BaseOAuth2:
    SCOPES = []
    CODE_URL = ''
    TOKEN_URL = ''
    INFO_URL = ''

    @classmethod
    def get_code_url(cls, redirect_uri: str) -> str:
        raise NotImplementedError

    @classmethod
    def get_access_token(cls, code: str, redirect_uri: str) -> Tuple[TokenResponse, dict]:
        raise NotImplementedError

    @classmethod
    def get_refresh_token(cls, refresh_token: str) -> Tuple[TokenResponse, dict]:
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
    def validate_token(cls, access_token: str) -> dict:
        raise NotImplementedError

    @classmethod
    def get_user_by_id(cls, db: Session, login_id: str) -> ORMUsers:
        raise NotImplementedError
