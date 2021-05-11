import pickle
import redis

from redis.lock import Lock
from typing import Any, List


class CacheNamespaceManager(object):
    def __init__(self, namespace: str, client: redis.StrictRedis):
        self.namespace = namespace
        self.client = client

    def _format_key(self, key: str) -> str:
        return f'{self.namespace}:{key}'

    def get_lock(self, key: str) -> Lock:
        return self.client.lock(f'lock:{self._format_key(key)}')

    def __getitem__(self, key: str) -> Any:
        return pickle.loads(self.client.get(self._format_key(key)))

    def __contains__(self, key: str) -> bool:
        return self.client.exists(self._format_key(key))

    def __setitem__(self, key: str, value: Any):
        self.client.set(self._format_key(key), pickle.dumps(value), ex=3600)

    def __delitem__(self, key: str):
        self.client.delete(self._format_key(key))
