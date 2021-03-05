import os

from os import environ


class Environment:
    SCHEME = environ.get("SCHEME", "http")
    HOST = environ.get("HOST", "127.0.0.1:5000")
    DB_USER = environ['DB_USER']
    DB_PASSWD = environ['DB_PASSWD']
    DB_HOST = environ['DB_HOST']
    DB_PORT = environ['DB_PORT']
    DB_NAME = environ['DB_NAME']


class Config:
    ROOT = os.path.abspath(os.path.dirname(__file__))
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = f'postgresql://{Environment.DB_USER}:{Environment.DB_PASSWD}@' \
                              f'{Environment.DB_HOST}:{Environment.DB_PORT}/{Environment.DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER_UI_REQUEST_DURATION = True
    ERROR_404_HELP = False
    CORS_SUPPORTS_CREDENTIALS = True

    HOST = f'{Environment.SCHEME}://{Environment.HOST}'

    URL_PREFIX = '/api'
    DOC_URL = '/swagger'
