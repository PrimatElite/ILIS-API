from collections import OrderedDict
from flask import redirect
from flask_restplus import Resource
from http import HTTPStatus

from ..models import Users
from ..models.enums import EnumLoginService, EnumUserRole
from ..oauth2 import get_service
from ..utils.swagger_models import AuthModels


api = AuthModels.api

_token_parser = api.parser()
_token_parser.add_argument('service', type=str, help='The login service.', location='args',
                           choices=list(EnumLoginService.__members__), required=True)
_token_parser.add_argument('grant_type', type=str, help='The grant type.', location='args',
                           choices=['authorization_code', 'refresh_token'], required=True)
_token_parser.add_argument('code', type=str, help='The authorization code.', location='args', store_missing=False)
_token_parser.add_argument('redirect_uri', type=str, help='The redirect uri.', location='args', store_missing=False)
_token_parser.add_argument('refresh_token', type=str, help='The refresh token.', location='args', store_missing=False)

_code_parser = api.parser()
_code_parser.add_argument('service', type=str, help='The login service.', location='args',
                          choices=list(EnumLoginService.__members__), required=True)
_code_parser.add_argument('redirect_uri', type=str, help='The redirect uri.', location='args', required=True)


@api.route('/code')
class AccessCodeApi(Resource):
    @api.doc('get_code_url')
    @api.expect(_code_parser)
    @api.response(303, 'See other')
    def get(self):
        args = _code_parser.parse_args()
        service = get_service(args['service'])
        return redirect(service.get_code_url(args['redirect_uri']), code=HTTPStatus.SEE_OTHER)


@api.route('/token')
class AccessTokenApi(Resource):
    @api.doc('get_token')
    @api.expect(_token_parser)
    @api.response(200, 'Success', AuthModels.access_token)
    @api.response(400, 'Bad request')
    @api.response(501, 'Not implemented')
    def post(self):
        args = _token_parser.parse_args()
        service = get_service(args['service'])

        token_response, user_info = None, None
        try:
            if args['grant_type'] == 'authorization_code':
                token_response, user_info = service.get_access_token(api, args['code'], args['redirect_uri'])
            else:
                token_response, user_info = service.get_refresh_token(api, args['refresh_token'])
        except KeyError as e:
            help_ = list(filter(lambda arg: arg.name == e.args[0], _token_parser.args))[0].help
            errors = {e.args[0]: f'{help_} Missing required parameter in the query string'}
            api.abort(HTTPStatus.BAD_REQUEST, 'Input payload validation failed', errors=errors)

        user = Users.get_user_by_login(service.get_id_from_info(user_info), args['service'])

        if user is None:
            data = service.transform_info(user_info)
            data['role'] = EnumUserRole.USER.name
            user = Users.create(data)

        access_token, refresh_token, expires_in = token_response
        return OrderedDict([('access_token', access_token), ('refresh_token', refresh_token),
                            ('expires_in', expires_in), ('user', user)])
