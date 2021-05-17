from .cache import Cache, is_cache_list
from ..redis import redis_client


cache = Cache(redis_client)


def init():
    cache.client.flushall()
