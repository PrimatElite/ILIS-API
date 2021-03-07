from flask_restplus import fields, Namespace

from ..models.enums import EnumLoginService, EnumUserRole


class DefaultModels:
    api = Namespace('default', description='Default operations')
    version = api.model('version', {
        'version': fields.String(required=True, description='The number of version')
    })


class UsersModels:
    api = Namespace('users', description='Users operations')
    create_user = api.model('create_user', {
        'login_id': fields.String(required=True, description='The user login identifier'),
        'login_type': fields.String(required=True, description='The user login service type',
                                    enum=list(EnumLoginService.__members__)),
        'name': fields.String(description='The user name'),
        'surname': fields.String(description='The user surname'),
        'role': fields.String(required=True, description='The user role', enum=list(EnumUserRole.__members__)),
        'email': fields.String(description='The user email'),
        'phone': fields.String(description='The user phone'),
        'avatar': fields.String(description='The user avatar')
    })
    update_user = api.model('update_user', {
        'name': fields.String(description='The user name'),
        'surname': fields.String(description='The user surname'),
        'role': fields.String(description='The user role', enum=list(EnumUserRole.__members__)),
        'email': fields.String(description='The user email'),
        'phone': fields.String(description='The user phone')
    })
    user = api.model('user', {
        'user_id': fields.Integer(required=True, description='The user identifier'),
        'login_id': fields.String(description='The user login identifier'),
        'login_type': fields.String(description='The user login service type', enum=list(EnumLoginService.__members__)),
        'name': fields.String(required=True, description='The user name'),
        'surname': fields.String(required=True, description='The user surname'),
        'role': fields.String(required=True, description='The user role', enum=list(EnumUserRole.__members__)),
        'email': fields.String(description='The user email'),
        'phone': fields.String(description='The user phone'),
        'avatar': fields.String(required=True, description='The user avatar'),
        'created_at': fields.DateTime(description='The user created datetime'),
        'updated_at': fields.DateTime(description='The user updated datetime')
    })


class AuthModels:
    api = Namespace('auth', description='Auth operations')
    access_token = api.model('access_token', {
        'access_token': fields.String(required=True, descriprion='The access token'),
        'refresh_token': fields.String(descriprion='The refresh token'),
        'expires_in': fields.Integer(description='The token expires in'),
        'user': fields.Nested(UsersModels.user, required=True, description='The user related to access token')
    })
