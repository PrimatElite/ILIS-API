from flask_restplus import Resource
from http import HTTPStatus

from ..models.orms.users import Users
from ..utils.swagger_models import UsersModels


api = UsersModels.api


@api.route('')
class UsersApi(Resource):
    @api.doc('get_users')
    @api.response(200, 'Success', [UsersModels.user])
    def get(self):
        """Get all users"""
        return Users.get_users()

    @api.doc('create_user')
    @api.expect(UsersModels.create_user, validate=True)
    @api.response(201, 'User created', UsersModels.user)
    @api.response(400, 'Bad request')
    def post(self):
        """Create new user"""
        user = Users.create(api.payload)
        return user, 201


@api.route('/<user_id>')
class UserByIdApi(Resource):
    @api.doc('get_user')
    @api.response(200, 'Success', UsersModels.user)
    @api.response(404, 'Not found')
    def get(self, user_id):
        """Get user by id"""
        user = Users.get_user_by_id(user_id)
        if user:
            return user
        api.abort(HTTPStatus.NOT_FOUND, f'User {user_id} not found')

    @api.doc('update_user')
    @api.expect(UsersModels.update_user, validate=True)
    @api.response(200, 'User updated', UsersModels.user)
    @api.response(400, 'Bad request')
    @api.response(404, 'Not found')
    def put(self, user_id):
        """Update user by id"""
        data = api.payload
        data['user_id'] = user_id
        user = Users.update(data)
        if user:
            return user
        api.abort(HTTPStatus.NOT_FOUND, f'User {user_id} not found')

    @api.doc('delete_user')
    @api.response(204, 'User deleted')
    @api.response(404, 'Not found')
    def delete(self, user_id):
        """Delete user by id"""
        user = Users.delete(user_id)
        if user:
            return user, 204
        api.abort(HTTPStatus.NOT_FOUND, f'User {user_id} not found')
