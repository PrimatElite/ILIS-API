import os

from dotenv import find_dotenv, load_dotenv
from os import environ
from pydantic import parse_raw_as
from typing import List


load_dotenv(find_dotenv())


class Environment:
    SCHEME = environ.get('SCHEME', 'http')
    HOST = environ.get('HOST', '127.0.0.1:5000')
    DB_USER = environ['DB_USER']
    DB_PASSWD = environ['DB_PASSWD']
    DB_HOST = environ['DB_HOST']
    DB_PORT = environ['DB_PORT']
    DB_NAME = environ['DB_NAME']
    LOG_ERRORS = parse_raw_as(bool, environ.get('LOG_ERRORS', 'false'))
    GOOGLE_CLIENT_SECRET = environ['GOOGLE_CLIENT_SECRET']
    VK_CLIENT_SECRET = environ['VK_CLIENT_SECRET']
    SECRET_KEY = environ['SECRET_KEY']
    REDIS_URL = environ.get('REDIS_URL', 'redis://127.0.0.1:6379')
    MAIL_USERNAME = environ['MAIL_USERNAME']
    MAIL_PASSWORD = environ['MAIL_PASSWORD']
    ELASTICSEARCH_URL = environ.get('ELASTICSEARCH_URL', 'elasticsearch://127.0.0.1:9200')
    CORS_ORIGINS = parse_raw_as(List[str], environ.get('CORS_ORIGINS', '[]'))


class Config:
    SQLALCHEMY_DATABASE_URI = f'postgresql://{Environment.DB_USER}:{Environment.DB_PASSWD}@' \
                              f'{Environment.DB_HOST}:{Environment.DB_PORT}/{Environment.DB_NAME}'
    CORS_ORIGINS = Environment.CORS_ORIGINS

    LOG_ERRORS = Environment.LOG_ERRORS

    HOST = f'{Environment.SCHEME}://{Environment.HOST}'

    URL_PREFIX = '/api'

    GOOGLE_CLIENT_ID = '674406560132-d8etms30a82chl3qb72o0ard0auha3b7.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = Environment.GOOGLE_CLIENT_SECRET

    VK_CLIENT_ID = '7783375'
    VK_CLIENT_SECRET = Environment.VK_CLIENT_SECRET

    SECRET_KEY = Environment.SECRET_KEY

    REDIS_URL = Environment.REDIS_URL

    ELASTICSEARCH_URL = Environment.ELASTICSEARCH_URL

    CELERY_BROKER_URL = REDIS_URL
    CELERY_IMPORTS = ['app.tasks']

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = Environment.MAIL_USERNAME
    MAIL_PASSWORD = Environment.MAIL_PASSWORD
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    REQUEST_MIN_DURATION_HOURS = 1
    REQUEST_MIN_DURATION_SECONDS = REQUEST_MIN_DURATION_HOURS * 3600
    NOTIFICATION_FACTOR = 5.0 / 6

    DATA_DIR = './data'

    IMAGES_WAY = 'images'
    IMAGES_DIR = os.path.join(DATA_DIR, IMAGES_WAY)
    IMAGES_TYPES = ['jpeg', 'png']
    MAX_IMAGE_LENGTH_MB = 10
    MAX_IMAGE_LENGTH_B = MAX_IMAGE_LENGTH_MB * 1024 * 1024
