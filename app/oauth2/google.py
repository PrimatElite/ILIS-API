import requests

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Tuple

from .base import BaseOAuth2, TokenResponse
from ..models import EnumLoginService, Users
from ..config import Config


class GoogleOAuth2(BaseOAuth2):
    SCOPES = [
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/userinfo.email'
    ]
    CODE_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    TOKEN_URL = 'https://oauth2.googleapis.com/token'
    INFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo?access_token='

    @classmethod
    def get_code_url(cls, redirect_uri: str) -> str:
        query_params = '&'.join([
            f'client_id={Config.GOOGLE_CLIENT_ID}',
            f'redirect_uri={redirect_uri}',
            'access_type=offline',
            'include_granted_scopes=true',
            'response_type=code',
            f'scope={" ".join(cls.SCOPES)}',
            'select_account=true'
        ])
        return f'{cls.CODE_URL}?{query_params}'

    @classmethod
    def get_access_token(cls, code: str, redirect_uri: str) -> Tuple[TokenResponse, dict]:
        query_params = '&'.join([
            f'client_id={Config.GOOGLE_CLIENT_ID}',
            f'client_secret={Config.GOOGLE_CLIENT_SECRET}',
            f'code={code}',
            'grant_type=authorization_code',
            f'redirect_uri={redirect_uri}'
        ])
        response = requests.post(f'{cls.TOKEN_URL}?{query_params}')
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(response.status_code)
        response_data = response.json()
        user_info = cls.get_info(response_data['access_token'])
        return TokenResponse(response_data['access_token'], response_data.get('refresh_token'),
                             response_data['expires_in']), user_info

    @classmethod
    def get_refresh_token(cls, refresh_token: str) -> Tuple[TokenResponse, dict]:
        query_params = '&'.join([
            f'client_id={Config.GOOGLE_CLIENT_ID}',
            f'client_secret={Config.GOOGLE_CLIENT_SECRET}',
            f'refresh_token={refresh_token}',
            'grant_type=authorization_code'
        ])
        response = requests.post(f'{cls.TOKEN_URL}?{query_params}')
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(response.status_code)
        response_data = response.json()
        user_info = cls.get_info(response_data['access_token'])
        return TokenResponse(response_data['access_token'], refresh_token, response_data['expires_in']), user_info

    @classmethod
    def get_info(cls, access_token: str) -> dict:
        response = requests.get(cls.INFO_URL + access_token)
        return response.json()

    @classmethod
    def get_id_from_info(cls, info: dict) -> str:
        return info['id']

    @classmethod
    def transform_info(cls, info: dict) -> dict:
        data = {
            'login_id': cls.get_id_from_info(info),
            'login_type': EnumLoginService.GOOGLE.name,
            'name': info['given_name'],
            'surname': info['family_name'],
            'email': info['email'],
            'avatar': info['picture']
        }
        ind = data['avatar'].find('s96-c')
        if ind > -1:
            avatar = data['avatar']
            data['avatar'] = avatar.replace('=s96-c', '') if avatar[ind - 1] == '=' else avatar.replace('s96-c', '')
        return data

    @classmethod
    def validate_token(cls, access_token: str) -> dict:
        response = requests.get(cls.INFO_URL + access_token)
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(response.status_code, response.text)
        response_data = response.json()
        if 'error' in response_data:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Invalid token supplied')
        return response_data

    @classmethod
    def get_user_by_id(cls, login_id: str, db: Session) -> Users:
        user = Users.get_user_by_login(login_id, EnumLoginService.GOOGLE.name, db)
        if user is not None:
            return user
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'User not found')
