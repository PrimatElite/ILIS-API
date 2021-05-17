import inspect

from functools import wraps
from itertools import chain
from redis import StrictRedis
from typing import Callable, List, Optional, Union

from .namespace import CacheNamespaceManager
from .value import ValueList, ValueObject


def _get_function_namespace(func: Callable):
    return f'{inspect.getmodule(func).__name__}|{func.__name__}'


def _has_function_self(func: Callable):
    args = list(inspect.signature(func).parameters)
    return args and args[0] in ('self', 'cls')


def _decorate_cache_element(decorator_args: tuple, cache: 'Cache') -> Callable:
    def decorate(func: Callable) -> Callable:
        namespace = _get_function_namespace(func)
        skip_self = _has_function_self(func)

        @wraps(func)
        def cached(*args, **kwargs) -> dict:
            cache_args = args
            if skip_self:
                cache_args = args[1:]
            cache_key = ' '.join(map(str, chain(decorator_args, cache_args)))

            def go():
                return func(*args, **kwargs)

            go.__name__ = f'_cached_{func.__name__}'

            return cache.get_value_object(cache_key, namespace, go).get_value()

        cached.__namespace__ = namespace
        cached.__key__ = ' '.join(map(str, decorator_args))
        return cached

    return decorate


def _decorate_cache_list(decorator_args: tuple, cache: 'Cache', field: str) -> Callable:
    def decorate(func: Callable) -> Callable:
        namespace = _get_function_namespace(func)
        skip_self = _has_function_self(func)

        @wraps(func)
        def cached(*args, **kwargs) -> List[dict]:
            cache_args = args
            if skip_self:
                cache_args = args[1:]
            cache_key = ' '.join(map(str, chain(decorator_args, cache_args)))

            def go():
                return func(*args, **kwargs)

            go.__name__ = f'_cached_{func.__name__}'

            return cache.get_value_list(cache_key, namespace, field, go).get_value()

        cached.__namespace__ = namespace
        cached.__key__ = ' '.join(map(str, decorator_args))
        cached.__field__ = field
        return cached

    return decorate


def is_cache_list(func: Callable):
    return hasattr(func, '__field__')


class Cache:
    managers = {}

    def __init__(self, client: StrictRedis):
        self.client = client

    def get_value_object(self, key: str, namespace: str, creation_func: Optional[Callable] = None) -> ValueObject:
        try:
            return ValueObject(key, Cache.managers[namespace], creation_func)
        except KeyError:
            Cache.managers[namespace] = CacheNamespaceManager(namespace, self.client)
            return ValueObject(key, Cache.managers[namespace], creation_func)

    def get_value_list(self, key: str, namespace: str, field: str,
                       creation_func: Optional[Callable] = None) -> ValueList:
        try:
            return ValueList(key, Cache.managers[namespace], field, creation_func)
        except KeyError:
            Cache.managers[namespace] = CacheNamespaceManager(namespace, self.client)
            return ValueList(key, Cache.managers[namespace], field, creation_func)

    def cache_element(self, *args) -> Callable:
        return _decorate_cache_element(args, self)

    def cache_list(self, *args, field: str) -> Callable:
        return _decorate_cache_list(args, self, field)

    def get_value_from_function(self, func: Callable, *args) -> Union[ValueList, ValueObject]:
        key = ' '.join(map(str, chain([func.__key__], args)))
        namespace = func.__namespace__
        if hasattr(func, '__field__'):
            return self.get_value_list(key, namespace, func.__field__)
        return self.get_value_object(key, namespace)
