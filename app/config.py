import os

from os import environ

from .utils import str2bool


class Environment:
    SCHEME = environ.get('SCHEME', 'http')
    HOST = environ.get('HOST', '127.0.0.1:5000')
    DB_USER = environ['DB_USER']
    DB_PASSWD = environ['DB_PASSWD']
    DB_HOST = environ['DB_HOST']
    DB_PORT = environ['DB_PORT']
    DB_NAME = environ['DB_NAME']
    LOG_ERRORS = str2bool(environ.get('LOG_ERRORS', 'False'))
    GOOGLE_CLIENT_SECRET = environ['GOOGLE_CLIENT_SECRET']
    VK_CLIENT_SECRET = environ['VK_CLIENT_SECRET']


class Config:
    ROOT = os.path.abspath(os.path.dirname(__file__))
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = f'postgresql://{Environment.DB_USER}:{Environment.DB_PASSWD}@' \
                              f'{Environment.DB_HOST}:{Environment.DB_PORT}/{Environment.DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER_UI_REQUEST_DURATION = True
    ERROR_404_HELP = False
    CORS_SUPPORTS_CREDENTIALS = True

    LOG_ERRORS = Environment.LOG_ERRORS

    HOST = f'{Environment.SCHEME}://{Environment.HOST}'

    URL_PREFIX = '/api'
    DOC_URL = '/swagger'

    GOOGLE_CLIENT_ID = '674406560132-d8etms30a82chl3qb72o0ard0auha3b7.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = Environment.GOOGLE_CLIENT_SECRET

    VK_CLIENT_ID = '7783375'
    VK_CLIENT_SECRET = Environment.VK_CLIENT_SECRET
