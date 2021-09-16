from sqlalchemy import Column
from typing import List

from .base import ORMBase


class ORMSearchable(ORMBase):
    __abstract__ = True

    __searchable__: List[Column] = []
