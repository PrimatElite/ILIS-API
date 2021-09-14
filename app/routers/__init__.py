from fastapi import FastAPI

from . import auth
from . import default
from . import items
from . import requests
from . import storages
from . import users


def init_app(app: FastAPI):
    app.include_router(default.router)
    app.include_router(auth.router)
    app.include_router(items.router)
    app.include_router(requests.router)
    app.include_router(storages.router)
    app.include_router(users.router)
