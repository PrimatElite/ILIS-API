from fastapi import FastAPI
from fastapi.routing import APIRouter

from . import auth, default, items, requests, storages, users
from ..config import Config


def init_app(app: FastAPI):
    router = APIRouter(prefix=Config.URL_PREFIX)
    router.include_router(default.router)
    router.include_router(auth.router)
    router.include_router(items.router)
    router.include_router(requests.router)
    router.include_router(storages.router)
    router.include_router(users.router)
    app.include_router(router)
