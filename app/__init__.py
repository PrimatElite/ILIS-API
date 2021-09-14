from fastapi import FastAPI

# from . import admin, cache, celery, mail  # TODO
from . import exceptions, routers, models
from .config import Config
from .utils import get_version


app = FastAPI(title='ILIS API', description='API for ILIS', version=get_version())


@app.on_event('startup')
async def startup_event():
    session = models.SessionLocal()
    models.Users.init(session)
    models.Items.reindex(session)
    session.close()


# mail.init_app(app)


def init_app() -> FastAPI:
    # CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)
    # cache.init()
    exceptions.init_app(app)
    routers.init_app(app)
    # admin.init_app(app)
    # celery.init()
    return app
