from flask_restplus import fields, Namespace


class DefaultModel:
    api = Namespace('default', description='Default operations')
    version = api.model('version', {
        'version': fields.String(required=True, description='The number of version')
    })
