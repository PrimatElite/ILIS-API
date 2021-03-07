import requests

from flask import current_app
from flask_restplus import Namespace
from http import HTTPStatus
from typing import Tuple

from .base import BaseOAuth2, TokenResponse
from ..models import Users
from ..models.enums import EnumLoginService


class VKOAuth2(BaseOAuth2):
    VK_SCOPES = ['offline', 'email']
    VK_CODE_URL = 'https://oauth.vk.com/authorize'
    VK_TOKEN_URL = 'https://oauth.vk.com/access_token'
    VK_INFO_URL = 'https://api.vk.com/method/users.get?v=5.52&fields=photo_200&access_token='

    @classmethod
    def get_code_url(cls, redirect_uri: str) -> str:
        query_params = '&'.join([
            f'client_id={current_app.config["VK_CLIENT_ID"]}',
            f'redirect_uri={redirect_uri}',
            'display=page',
            'response_type=code',
            f'scope={",".join(cls.VK_SCOPES)}',
            'v=5.52'
        ])
        return f'{cls.VK_CODE_URL}?{query_params}'

    @classmethod
    def get_access_token(cls, api: Namespace, code: str, redirect_uri: str) -> Tuple[TokenResponse, dict]:
        query_params = '&'.join([
            f'client_id={current_app.config["VK_CLIENT_ID"]}',
            f'client_secret={current_app.config["VK_CLIENT_SECRET"]}',
            f'code={code}',
            f'redirect_uri={redirect_uri}'
        ])
        response = requests.post(f'{cls.VK_TOKEN_URL}?{query_params}')
        if response.status_code != HTTPStatus.OK:
            api.abort(response.status_code)
        response_data = response.json()
        user_info = cls.get_info(response_data['access_token'])
        user_info['email'] = response_data['email']
        return TokenResponse(response_data['access_token'], None, response_data['expires_in']), user_info

    @classmethod
    def get_refresh_token(cls, api: Namespace, refresh_token: str):
        api.abort(HTTPStatus.NOT_IMPLEMENTED, 'There is no functionality for VK service')

    @classmethod
    def get_info(cls, access_token: str) -> dict:
        response = requests.get(cls.VK_INFO_URL + access_token)
        return response.json()['response'][0]

    @classmethod
    def get_id_from_info(cls, info: dict) -> str:
        return str(info['id'])

    @classmethod
    def transform_info(cls, info: dict) -> dict:
        data = {
            'login_id': cls.get_id_from_info(info),
            'login_type': EnumLoginService.VK.name,
            'name': info['first_name'],
            'surname': info['last_name'],
            'avatar': info['photo_200']
        }
        if 'email' in info:
            data['email'] = info['email']
        return data

    @classmethod
    def validate_token(cls, api: Namespace, access_token: str) -> dict:
        response = requests.get(cls.VK_INFO_URL + access_token)
        if response.status_code != HTTPStatus.OK:
            api.abort(response.status_code, response.text)
        response_data = response.json()
        if 'error' in response_data:
            api.abort(HTTPStatus.UNAUTHORIZED, 'Invalid token supplied')
        return response_data['response'][0]

    @classmethod
    def get_user_by_id(cls, api: Namespace, login_id: str) -> dict:
        user = Users.get_user_by_login(login_id, EnumLoginService.VK.name)
        if user is not None:
            return user
        api.abort(HTTPStatus.NOT_FOUND, 'User not found')
