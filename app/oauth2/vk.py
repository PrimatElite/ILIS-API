import requests

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Tuple

from .base import BaseOAuth2, TokenResponse
from ..services import Users
from ..models import EnumLoginService, ORMUsers
from ..config import Config


class VKOAuth2(BaseOAuth2):
    SCOPES = ['offline', 'email']
    CODE_URL = 'https://oauth.vk.com/authorize'
    TOKEN_URL = 'https://oauth.vk.com/access_token'
    INFO_URL = 'https://api.vk.com/method/users.get?v=5.52&fields=photo_max&access_token='

    @classmethod
    def get_code_url(cls, redirect_uri: str) -> str:
        query_params = '&'.join([
            f'client_id={Config.VK_CLIENT_ID}',
            f'redirect_uri={redirect_uri}',
            'display=page',
            'response_type=code',
            f'scope={",".join(cls.SCOPES)}',
            'v=5.52'
        ])
        return f'{cls.CODE_URL}?{query_params}'

    @classmethod
    def get_access_token(cls, code: str, redirect_uri: str) -> Tuple[TokenResponse, dict]:
        query_params = '&'.join([
            f'client_id={Config.VK_CLIENT_ID}',
            f'client_secret={Config.VK_CLIENT_SECRET}',
            f'code={code}',
            f'redirect_uri={redirect_uri}'
        ])
        response = requests.post(f'{cls.TOKEN_URL}?{query_params}')
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(response.status_code)
        response_data = response.json()
        user_info = cls.get_info(response_data['access_token'])
        user_info['email'] = response_data['email']
        return TokenResponse(response_data['access_token'], None, response_data['expires_in']), user_info

    @classmethod
    def get_refresh_token(cls, refresh_token: str):
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, 'There is no functionality for VK service')

    @classmethod
    def get_info(cls, access_token: str) -> dict:
        response = requests.get(cls.INFO_URL + access_token)
        return response.json()['response'][0]

    @classmethod
    def get_id_from_info(cls, info: dict) -> str:
        return str(info['id'])

    @classmethod
    def transform_info(cls, info: dict) -> dict:
        data = {
            'login_id': cls.get_id_from_info(info),
            'login_type': EnumLoginService.VK,
            'name': info['first_name'],
            'surname': info['last_name'],
            'avatar': info['photo_max']
        }
        if 'email' in info:
            data['email'] = info['email']
        return data

    @classmethod
    def validate_token(cls, access_token: str) -> dict:
        response = requests.get(cls.INFO_URL + access_token)
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(response.status_code, response.text)
        response_data = response.json()
        if 'error' in response_data:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Invalid token supplied')
        return response_data['response'][0]

    @classmethod
    def get_user_by_id(cls, db: Session, login_id: str) -> ORMUsers:
        user = Users.get_user_by_login(db, login_id, EnumLoginService.VK)
        if user is not None:
            return user
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'User not found')
