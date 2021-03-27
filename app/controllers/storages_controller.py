from flask_restplus import marshal, Resource
from http import HTTPStatus

from ..models import Storages, Users
from ..utils.auth import check_admin, get_user_from_request, token_required
from ..utils.swagger import delete_object_by_id
from ..utils.swagger_models import StoragesModels


api = StoragesModels.api


@api.route('')
@api.doc(security='access-token')
class StoragesApi(Resource):
    @api.doc('get_storages')
    @api.response(200, 'Success', [StoragesModels.storage])
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @token_required
    def get(self):
        """Get all storages"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        return Storages.get_storages()

    @api.doc('create_storage')
    @api.expect(StoragesModels.create_storage, validate=True)
    @api.response(201, 'Storage created', StoragesModels.storage)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def post(self):
        """Create new storage"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        data = marshal(api.payload, StoragesModels.create_storage, skip_none=True)
        storage = Storages.create(data)
        if storage is not None:
            return storage, 201
        api.abort(HTTPStatus.NOT_FOUND, f'User {data["user_id"]} not found')

    @api.doc('update_storage')
    @api.expect(StoragesModels.update_storage, validate=True)
    @api.response(200, 'Storage updated', StoragesModels.storage)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def put(self):
        """Update storage"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        data = marshal(api.payload, StoragesModels.update_storage, skip_none=True)
        storage = Storages.update(data)
        if storage is not None:
            return storage
        api.abort(HTTPStatus.NOT_FOUND, f'Storage {data["storage_id"]} not found')


@api.route('/<int:storage_id>')
@api.doc(security='access-token')
class StoragesByIdApi(Resource):
    @api.doc('delete_storage_by_id')
    @api.response(204, 'Storage deleted')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def delete(self, storage_id: int):
        """Delete storage by id"""
        return delete_object_by_id(api, Storages, storage_id)


@api.route('/me')
@api.doc(security='access-token')
class StoragesMeApi(Resource):
    @api.doc('get_storages_me')
    @api.response(200, 'Success', [StoragesModels.storage])
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def get(self):
        """Get own storages"""
        user = get_user_from_request(api)
        return Storages.get_storages_by_user(user['user_id'])

    @api.doc('create_storage_me')
    @api.expect(StoragesModels.create_storage_me, validate=True)
    @api.response(201, 'Storage created', StoragesModels.storage)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def post(self):
        """Create new own storage"""
        requester = get_user_from_request(api)
        storage = marshal(api.payload, StoragesModels.create_storage_me, skip_none=True)
        storage['user_id'] = requester['user_id']
        return Storages.create(storage), 201

    @api.doc('update_storage_me')
    @api.expect(StoragesModels.update_storage_me, validate=True)
    @api.response(200, 'Storage updated', StoragesModels.storage)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def put(self):
        """Update own storage"""
        requester = get_user_from_request(api)
        data = marshal(api.payload, StoragesModels.update_storage_me, skip_none=True)
        storage = Storages.get_storage_by_id(data['storage_id'])
        if storage is not None:
            if requester['user_id'] == storage['user_id']:
                storage = Storages.update(data)
                return storage
            else:
                api.abort(HTTPStatus.FORBIDDEN, f'Storage {data["storage_id"]} is not yours')
        api.abort(HTTPStatus.NOT_FOUND, f'Storage {data["storage_id"]} not found')


@api.route('/me/<int:storage_id>')
class StoragesMeByIdApi(Resource):
    @api.doc('delete_me_storage_by_id', security='access-token')
    @api.response(204, 'Storage deleted')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def delete(self, storage_id: int):
        """Delete own storage by id"""
        requester = get_user_from_request(api)
        storage = Storages.get_storage_by_id(storage_id)
        if storage is not None:
            if requester['user_id'] == storage['user_id']:
                ret = Storages.delete(storage_id)
                if ret:
                    return '', 204
                api.abort(HTTPStatus.FORBIDDEN, f'Storage {storage_id} can\'t be deleted')
            api.abort(HTTPStatus.FORBIDDEN, f'Storage {storage_id} is not yours')
        api.abort(HTTPStatus.NOT_FOUND, f'Storage {storage_id} not found')


@api.route('/user/<int:user_id>')
@api.doc(security='access-token')
class StoragesByUserApi(Resource):
    @api.doc('get_storages_by_user')
    @api.response(200, 'Success', [StoragesModels.storage])
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def get(self, user_id: int):
        """Get storages by user"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        user = Users.get_user_by_id(user_id)
        if user is not None:
            return Storages.get_storages_by_user(user['user_id'])
        api.abort(HTTPStatus.NOT_FOUND, f'User {user_id} not found')
