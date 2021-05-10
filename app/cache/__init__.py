from flask import Flask

from .cache import Cache, is_cache_list


cache = Cache()


def init_app(app: Flask):
    if app.config['REDIS_URL']:
        cache.update_client(app.config['REDIS_URL'])
