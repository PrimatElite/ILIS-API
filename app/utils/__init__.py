import json
import os

from datetime import datetime
from dateutil import parser
from typing import Iterable


def get_version() -> str:
    with open('VERSION') as version_file:
        version = version_file.read()
    return version.strip()


def get_db_initialization() -> dict:
    with open(os.path.join('app', 'models', 'db_initialization.json')) as db_initialization_file:
        return json.load(db_initialization_file)


def datetime2str(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def str2datetime(value: str) -> datetime:
    return parser.parse(value)


def any_in(params: Iterable, data: Iterable) -> bool:
    return any(p in data for p in params)


def all_in(params: Iterable, data: Iterable) -> bool:
    return all(p in data for p in params)
