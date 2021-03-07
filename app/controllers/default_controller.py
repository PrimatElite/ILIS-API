from flask_restplus import Resource

from ..utils import get_version
from ..utils.swagger_models import DefaultModels


api = DefaultModels.api


@api.route('version')
class VersionApi(Resource):
    @api.doc('get_version')
    @api.response(200, 'Success', DefaultModels.version)
    def get(self):
        """Get number of version"""
        return {'version': get_version()}
