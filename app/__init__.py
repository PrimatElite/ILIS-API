from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from . import admin, cache, celery, mail  # TODO
from . import cruds, exceptions, models, routers
from .config import Config
from .utils import get_version


app = FastAPI(title='ILIS API', description='API for ILIS', version=get_version(),
              openapi_url=f'{Config.URL_PREFIX}/openapi.json')


@app.on_event('startup')
async def startup_event():
    session = models.SessionLocal()
    cruds.CRUDUsers.init(session)
    cruds.CRUDItems.reindex(session)
    session.close()


# mail.init_app(app)


def init_app() -> FastAPI:
    if len(Config.CORS_ORIGINS) > 0:
        app.add_middleware(CORSMiddleware, allow_origins=Config.CORS_ORIGINS, allow_credentials=True,
                           allow_methods=["*"], allow_headers=["*"])
    # cache.init()
    exceptions.init_app(app)
    routers.init_app(app)
    # admin.init_app(app)
    # celery.init()
    return app
