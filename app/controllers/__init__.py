from flask import Blueprint, Flask, url_for
from flask_restplus import Api, fields
from flask_restplus.apidoc import apidoc
from jsonschema import FormatChecker

from . import auth_controller
from . import default_controller
from . import items_controller
from . import requests_controller
from . import storages_controller
from . import users_controller
from ..config import Environment
from ..utils import get_version


def validate_datetime(instance: str):
    if not isinstance(instance, str):
        return False
    return fields.datetime_from_iso8601(instance)


FormatChecker.cls_checks('date-time', ValueError)(validate_datetime)


class ApiScheme(Api):
    @property
    def specs_url(self):
        scheme = Environment.SCHEME
        return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)


AUTHORIZATIONS = {
    'access-token': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'authorization'
    }
}


def init_app(app: Flask):
    apidoc.url_prefix = app.config['URL_PREFIX']
    blueprint = Blueprint('api', __name__, url_prefix=app.config['URL_PREFIX'])
    api = ApiScheme(blueprint, version=get_version(), title='ILIS API', description='API for ILIS',
                    doc=app.config['DOC_URL'], authorizations=AUTHORIZATIONS,
                    format_checker=FormatChecker(formats=['date-time']))

    api.add_namespace(default_controller.api, path='/')
    api.add_namespace(auth_controller.api)
    api.add_namespace(items_controller.api)
    api.add_namespace(requests_controller.api)
    api.add_namespace(storages_controller.api)
    api.add_namespace(users_controller.api)

    app.register_blueprint(blueprint)
