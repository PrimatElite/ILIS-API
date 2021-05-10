from collections import OrderedDict
from typing import Callable, List, Optional

from .namespace import CacheNamespaceManager


class ValueObject:
    def __init__(self, key: str, namespace: CacheNamespaceManager, creation_func: Optional[Callable] = None):
        self.key = key
        self.creation_func = creation_func
        self.namespace = namespace

    def get_value(self) -> dict:
        with self.namespace.get_lock(self.key):
            if self.key in self.namespace:
                return self.namespace[self.key]
            self.namespace[self.key] = obj = self.creation_func()
            return obj

    def update_value(self, new_value: dict):
        with self.namespace.get_lock(self.key):
            if self.key in self.namespace:
                self.namespace[self.key] = new_value

    def delete_value(self):
        with self.namespace.get_lock(self.key):
            if self.key in self.namespace:
                del self.namespace[self.key]


class ValueList:
    def __init__(self, key: str, namespace: CacheNamespaceManager, field: str,
                 creation_func: Optional[Callable] = None):
        self.key = key
        self.creation_func = creation_func
        self.namespace = namespace
        self.field = field

    def get_value(self) -> List[dict]:
        with self.namespace.get_lock(self.key):
            if self.key in self.namespace:
                return list(self.namespace[self.key].values())
            obj = self.creation_func()
            self.namespace[self.key] = OrderedDict([(element[self.field], element) for element in obj])
            return obj

    def update_value(self, element: dict):
        with self.namespace.get_lock(self.key):
            if self.key in self.namespace:
                obj = self.namespace[self.key]
                obj[element[self.field]] = element
                self.namespace[self.key] = obj

    def delete_element(self, element: dict):
        with self.namespace.get_lock(self.key):
            if self.key in self.namespace:
                obj = self.namespace[self.key]
                del obj[element[self.field]]
                self.namespace[self.key] = obj
