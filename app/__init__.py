from flask_cors import CORS
from flask import Flask

from . import controllers, models
from .config import Config


def create_flask_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    return app


def create_app():
    app = create_flask_app()
    CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)
    controllers.init_app(app)
    models.init_app(app)
    return app
