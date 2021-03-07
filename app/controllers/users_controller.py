from flask_restplus import marshal, Resource
from http import HTTPStatus

from ..models import Users
from ..utils.auth import check_admin, get_service_from_request, get_token_from_request, get_user_from_request, \
    token_required
from ..utils.swagger_models import UsersModels


api = UsersModels.api


@api.route('')
@api.doc(security='access-token')
class UsersApi(Resource):
    @api.doc('get_users')
    @api.response(200, 'Success', [UsersModels.user])
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @token_required
    def get(self):
        """Get all users"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        return Users.get_users()

    @api.doc('create_user')
    @api.expect(UsersModels.create_user, validate=True)
    @api.response(201, 'User created', UsersModels.user)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @token_required
    def post(self):
        """Create new user"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        user = Users.create(marshal(api.payload, UsersModels.create_user, skip_none=True))
        return user, 201

    @api.doc('update_user')
    @api.expect(UsersModels.update_user, validate=True)
    @api.response(200, 'User updated', UsersModels.user)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def put(self):
        """Update user"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        data = marshal(api.payload, UsersModels.update_user, skip_none=True)
        user = Users.update(data)
        if user:
            return user
        api.abort(HTTPStatus.NOT_FOUND, f'User {data["user_id"]} not found')


@api.route('/me')
@api.doc(security='access-token')
class UsersMeApi(Resource):
    @api.doc('get_user_me')
    @api.response(200, 'Success', UsersModels.user)
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def get(self):
        """Get user by token"""
        service = get_service_from_request()
        validation_data = service.validate_token(api, get_token_from_request())
        user = service.get_user_by_id(api, service.get_id_from_info(validation_data))
        data = service.transform_info(validation_data)

        data_to_update = {field: value for field, value in data.items() if user[field] is None}
        if data['avatar'] != user['avatar']:
            data_to_update['avatar'] = data['avatar']
        if len(data_to_update) > 0:
            data_to_update['user_id'] = user['user_id']
            user = Users.update(data_to_update)
        return user

    @api.doc('update_user_me')
    @api.expect(UsersModels.update_user_me, validate=True)
    @api.response(200, 'User updated', UsersModels.user)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def put(self):
        """Update user by token"""
        requester = get_user_from_request(api)
        data = marshal(api.payload, UsersModels.update_user_me, skip_none=True)
        data['user_id'] = requester['user_id']
        return Users.update(data)


@api.route('/<int:user_id>')
class UsersByIdApi(Resource):
    @api.doc('get_user_by_id')
    @api.response(200, 'Success', UsersModels.user_public)
    @api.response(404, 'Not found')
    def get(self, user_id: int):
        """Get user by id"""
        user = Users.get_user_by_id(user_id)
        if user is not None:
            return marshal(user, UsersModels.user_public)
        api.abort(HTTPStatus.NOT_FOUND, f'User {user_id} not found')

    @api.doc('delete_user_by_id', security='access-token')
    @api.response(204, 'User deleted')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def delete(self, user_id: int):
        """Delete user by id"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        user = Users.delete(user_id)
        if user:
            return '', 204
        api.abort(HTTPStatus.NOT_FOUND, f'User {user_id} not found')
