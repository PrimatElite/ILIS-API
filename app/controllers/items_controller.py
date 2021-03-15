from flask_restplus import marshal, Resource
from http import HTTPStatus

from ..models import Items, Storages
from ..utils.auth import check_admin, get_user_from_request, token_required
from ..utils.swagger_models import ItemsModels


api = ItemsModels.api


@api.route('')
@api.doc(security='access-token')
class ItemsApi(Resource):
    @api.doc('get_items')
    @api.response(200, 'Success', [ItemsModels.item])
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @token_required
    def get(self):
        """Get all items"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        return Items.get_items()

    @api.doc('create_item')
    @api.expect(ItemsModels.create_item, validate=True)
    @api.response(201, 'Item created', ItemsModels.item)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def post(self):
        """Create new item"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        data = marshal(api.payload, ItemsModels.create_item, skip_none=True)
        item = Items.create(data)
        if item is not None:
            return item, 201
        api.abort(HTTPStatus.NOT_FOUND, f'Storage {data["storage_id"]} not found')

    @api.doc('update_item')
    @api.expect(ItemsModels.update_item, validate=True)
    @api.response(200, 'Item updated', ItemsModels.item)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def put(self):
        """Update item"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        data = marshal(api.payload, ItemsModels.update_item, skip_none=True)
        item = Items.update(data)
        if item is not None:
            return item
        api.abort(HTTPStatus.NOT_FOUND, f'Item {data["item_id"]} not found')


@api.route('/<int:item_id>')
class ItemsByIdApi(Resource):
    @api.doc('get_item_by_id')
    @api.response(200, 'Success', ItemsModels.item_public)
    @api.response(404, 'Not found')
    def get(self, item_id: int):
        """Get item by id"""
        from ..models import Users
        item = Items.get_item_by_id(item_id)
        storage = Storages.get_storage_by_id(item['storage_id'])
        user = Users.get_user_by_id(storage['user_id'])
        if item is not None:
            united = user.copy()
            united.update(item)
            res = marshal(united, ItemsModels.item_public)
            return res
        api.abort(HTTPStatus.NOT_FOUND, f'Item {item_id} not found')

    @api.doc('delete_item_by_id', security='access-token')
    @api.response(204, 'User deleted')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def delete(self, item_id: int):
        """Delete item by id"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        item = Items.delete(item_id)
        if item is not None:
            if item:
                return '', 204
            api.abort(HTTPStatus.FORBIDDEN, f'Item {item_id} can\'t be deleted')
        api.abort(HTTPStatus.NOT_FOUND, f'Item {item_id} not found')


@api.route('/me')
@api.doc(security='access-token')
class ItemsMeApi(Resource):
    @api.doc('create_item_in_storage_me')
    @api.expect(ItemsModels.create_item, validate=True)
    @api.response(201, 'Item created', ItemsModels.item)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def post(self):
        """Create new item in own storage"""
        user = get_user_from_request(api)
        item = marshal(api.payload, ItemsModels.create_item, skip_none=True)
        storage = Storages.get_storage_by_id(item['storage_id'])
        if storage is not None:
            if user['user_id'] == storage['user_id']:
                item['storage_id'] = storage['storage_id']
                return Items.create(item), 201
            api.abort(HTTPStatus.FORBIDDEN, f'Storage {item["storage_id"]} is not yours')
        api.abort(HTTPStatus.NOT_FOUND, f'Storage {item["storage_id"]} not found')

    @api.doc('update_item_me')
    @api.expect(ItemsModels.update_item, validate=True)
    @api.response(200, 'Item updated', ItemsModels.item)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def put(self):
        """Update item in own storage"""
        user = get_user_from_request(api)
        data = marshal(api.payload, ItemsModels.update_item, skip_none=True)
        item = Items.get_item_by_id(data['item_id'])
        if item is not None:
            start_storage = Storages.get_storage_by_id(item['storage_id'])
            if user['user_id'] == start_storage['user_id']:
                dest_storage = Storages.get_storage_by_id(data['storage_id'])
                if dest_storage is not None:
                    if user['user_id'] == dest_storage['user_id']:
                        item = Items.update(data)
                        return item
                    api.abort(HTTPStatus.FORBIDDEN, f'Storage {data["storage_id"]} is not yours')
                api.abort(HTTPStatus.NOT_FOUND, f'Storage {data["storage_id"]} not found')
            api.abort(HTTPStatus.FORBIDDEN, f'Item {data["item_id"]} is not yours')
        api.abort(HTTPStatus.NOT_FOUND, f'Item {data["item_id"]} not found')

@api.route('/me/storage/<int:storage_id>')
@api.doc(security='access-token')
class ItemsMeByStorageIdApi(Resource):
    @api.doc('get_items_by_storage_me')
    @api.response(200, 'Success', [ItemsModels.item])
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def get(self, storage_id: int):
        """Get items from own storage"""
        user = get_user_from_request(api)
        storage = Storages.get_storage_by_id(storage_id)
        if storage is not None:
            if user['user_id'] == storage['user_id']:
                return Items.get_items_by_storage(storage['storage_id'])
            api.abort(HTTPStatus.FORBIDDEN, f'Storage {storage_id} is not yours')
        api.abort(HTTPStatus.NOT_FOUND, f'Storage {storage_id} not found')


@api.route('/me/<int:item_id>')
@api.doc(security='access-token')
class ItemsMeByIdApi(Resource):
    @api.doc('delete_me_item_by_id', security='access-token')
    @api.response(204, 'Item deleted')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def delete(self, item_id: int):
        """Delete item in own storage by id"""
        user = get_user_from_request(api)
        item = Items.get_item_by_id(item_id)
        if item is not None:
            storage = Storages.get_storage_by_id(item['storage_id'])
            if user['user_id'] == storage['user_id']:
                item_response = Items.delete(item_id)
                if item_response:
                    return '', 204
                api.abort(HTTPStatus.FORBIDDEN, f'Item {item_id} can\'t be deleted')
            api.abort(HTTPStatus.FORBIDDEN, f'Item {item_id} is not yours')
        api.abort(HTTPStatus.NOT_FOUND, f'Item {item_id} not found')


@api.route('/storage/<int:storage_id>')
@api.doc(security='access-token')
class ItemsMeByStorageIdApi(Resource):
    @api.doc('get_items_by_storage')
    @api.response(200, 'Success', [ItemsModels.item])
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def get(self, storage_id: int):
        """Get items by storage"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        storage = Storages.get_storage_by_id(storage_id)
        if storage is not None:
            return Items.get_items_by_storage(storage['storage_id'])
        api.abort(HTTPStatus.NOT_FOUND, f'Storage {storage_id} not found')
