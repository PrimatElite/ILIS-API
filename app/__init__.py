from flask import Flask
from flask_cors import CORS

from . import controllers, models
from .config import Config


def create_flask_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    return app


def create_app() -> Flask:
    app = create_flask_app()
    CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)
    controllers.init_app(app)
    models.init_app(app)
    return app
