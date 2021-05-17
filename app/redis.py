from redis import StrictRedis

from .config import Config


redis_client = StrictRedis.from_url(Config.REDIS_URL)
