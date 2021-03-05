from flask import Blueprint, url_for
from flask_restplus import Api, fields
from flask_restplus.apidoc import apidoc
from jsonschema import FormatChecker

from . import default_controller
from ..utils import get_version
from ..config import Environment


def validate_datetime(instance):
    if not isinstance(instance, str):
        return False
    return fields.date_from_iso8601(instance)


FormatChecker.cls_checks('date-time', ValueError)(validate_datetime)


class ApiScheme(Api):
    @property
    def specs_url(self):
        scheme = Environment.SCHEME
        return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)


AUTHORIZATIONS = {}


def init_app(app):
    apidoc.url_prefix = app.config['URL_PREFIX']
    blueprint = Blueprint('api', __name__, url_prefix=app.config['URL_PREFIX'])
    api = ApiScheme(blueprint, version=get_version(), title='ILIS API', description='API for ILIS',
                    doc=app.config['DOC_URL'], authorizations=AUTHORIZATIONS,
                    format_checker=FormatChecker(formats=['date-time']))

    api.add_namespace(default_controller.api, path='/')

    app.register_blueprint(blueprint)
