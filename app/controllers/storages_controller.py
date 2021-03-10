from flask_restplus import marshal, Resource
from http import HTTPStatus

from ..models import Users, Storages
from ..utils.auth import check_admin, get_user_from_request, token_required
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
    @token_required
    def post(self):
        """Create new storage"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        storage = Storages.create(marshal(api.payload, StoragesModels.storage, skip_none=True))
        return storage, 201

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
        if storage:
            return storage
        api.abort(HTTPStatus.NOT_FOUND, f'Storage {data["storage_id"]} not found')


@api.route('/<int:storage_id>')
@api.doc(security='access-token')
class StorageByIdApi(Resource):
    @api.doc('delete_storage_by_id')
    @api.response(204, 'Storage deleted')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def delete(self, storage_id: int):
        """Delete storage by id"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        storage = Storages.delete(storage_id)
        if storage:
            return '', 204
        api.abort(HTTPStatus.NOT_FOUND, f'Storage {storage_id} not found')


@api.route('/me')
@api.doc(security='access-token')
class StoragesMeApi(Resource):
    @api.doc('get_storage_me')
    @api.response(200, 'Success', [StoragesModels.storage])
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def get(self):
        """Get storage by user"""
        user = get_user_from_request(api)
        if user:
            return Storages.get_storages_by_user(user['user_id'])
        return '', 401

    @api.doc('update_storage_me')
    @api.expect(StoragesModels.update_storage_me, validate=True)
    @api.response(200, 'Storage updated', StoragesModels.storage)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def put(self):
        """Update storage by user"""
        requester = get_user_from_request(api)
        data = marshal(api.payload, StoragesModels.update_storage_me, skip_none=True)
        data['user_id'] = requester['user_id']
        return Storages.update(data)

    @api.doc('create_storage_me')
    @api.expect(StoragesModels.create_storage_me, validate=True)
    @api.response(201, 'Storage created', StoragesModels.storage)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def post(self):
        """Create new storage"""
        requester = get_user_from_request(api)
        storage = marshal(api.payload, StoragesModels.create_storage_me, skip_none=True)
        storage['user_id'] = requester['user_id']
        Storages.create(storage)
        return storage, 201

@api.route('/me/<int:storage_id>')
@api.doc(security='access-token')
class StorageMeByIdApi(Resource):
    @api.doc('delete_own_storage_by_id', security='access-token')
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
                storage = Storages.delete(storage_id)
                return '', 204
        if storage:
            api.abort(HTTPStatus.FORBIDDEN, f'Storage {storage_id} is not yours')
        api.abort(HTTPStatus.NOT_FOUND, f'Storage {storage_id} not found')


@api.route('/user/<int:user_id>')
@api.doc(security='access-token')
class StoragesByUserApi(Resource):
    @api.doc('get_storages_by_user')
    @api.response(200, 'Success', [StoragesModels.storage])
    @api.response(404, 'Not found')
    def get(self, user_id: int):
        """Get storages by user"""
        user = Users.get_user_by_id(user_id)
        if user is not None:
            return Storages.get_storages_by_user(user['user_id'])
        api.abort(HTTPStatus.NOT_FOUND, f'User {user_id} not found')
