from flask import Flask
from flask_cors import CORS

from . import admin, cache, celery, controllers, mail, models
from .config import Config


app = Flask(__name__)
app.config.from_object(Config)

models.init_app(app)
mail.init_app(app)


def init_app() -> Flask:
    CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)
    cache.init()
    controllers.init_app(app)
    admin.init_app(app)
    celery.init()
    return app
