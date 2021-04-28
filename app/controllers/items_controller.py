from collections import OrderedDict
from flask_restplus import marshal, Resource
from http import HTTPStatus
from sqlalchemy import or_
from werkzeug.datastructures import FileStorage

from ..models import Images, Items, Storages, Users
from ..utils.auth import check_admin, get_user_from_request, token_required
from ..utils.images import get_file_dest
from ..utils.swagger import delete_object_by_id, get_object_with_additional_fields, get_objects_with_additional_fields
from ..utils.swagger_models import ImagesModels, ItemsModels


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
        return get_objects_with_additional_fields(Items.get_items(), Items)

    @api.doc('create_item')
    @api.expect(ItemsModels.create_item_with_images, validate=True)
    @api.response(201, 'Item created', [ItemsModels.item, [ImagesModels.image]])
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def post(self):
        """Create new item"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        args = ItemsModels.create_item_with_images.parse_args()

        time = Items.now().replace(microsecond=0).isoformat()
        t = time.replace(':', '-')
        files = []

        data = OrderedDict([])
        for item_arg in args:
            if item_arg in ItemsModels.item:
                data[item_arg] = args[item_arg]
            if type(args[item_arg]) is FileStorage:
                files.append(args[item_arg])

        item = Items.create(data)
        if item is not None:
            images = []
            for img in files:
                file = get_file_dest(api, img, t)
                data_img = OrderedDict([])
                data_img['item_id'] = item['item_id']
                data_img['path'] = file
                image = Images.create(data_img)
                images.append(image)
                img.save(file)
            return [get_object_with_additional_fields(item, Items), images], 201
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
            return get_object_with_additional_fields(item, Items)
        api.abort(HTTPStatus.NOT_FOUND, f'Item {data["item_id"]} not found')


@api.route('/<int:item_id>')
class ItemsByIdApi(Resource):
    @api.doc('get_item_by_id')
    @api.response(200, 'Success', ItemsModels.item_public)
    @api.response(404, 'Not found')
    def get(self, item_id: int):
        """Get item by id"""
        item = Items.get_item_by_id(item_id)
        if item is not None:
            storage = Storages.get_storage_by_id(item['storage_id'])
            user = Users.get_user_by_id(storage['user_id'])
            united = OrderedDict([('owner', user)])
            united.update(get_object_with_additional_fields(item, Items))
            res = marshal(united, ItemsModels.item_public)
            return res
        api.abort(HTTPStatus.NOT_FOUND, f'Item {item_id} not found')

    @api.doc('delete_item_by_id', security='access-token')
    @api.response(204, 'Item deleted')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def delete(self, item_id: int):
        """Delete item by id"""
        return delete_object_by_id(api, Items, item_id)


@api.route('/me')
@api.doc(security='access-token')
class ItemsMeApi(Resource):
    @api.doc('create_item_me')
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
        data = marshal(api.payload, ItemsModels.create_item, skip_none=True)
        storage = Storages.get_storage_by_id(data['storage_id'])
        if storage is not None:
            if user['user_id'] == storage['user_id']:
                data['storage_id'] = storage['storage_id']
                item = Items.create(data)
                return get_object_with_additional_fields(item, Items), 201
            api.abort(HTTPStatus.FORBIDDEN, f'Storage {data["storage_id"]} is not yours')
        api.abort(HTTPStatus.NOT_FOUND, f'Storage {data["storage_id"]} not found')

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
                item = Items.update(data)
                return get_object_with_additional_fields(item, Items)
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
                return get_objects_with_additional_fields(Items.get_items_by_storage(storage['storage_id']), Items)
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
            return get_objects_with_additional_fields(Items.get_items_by_storage(storage['storage_id']), Items)
        api.abort(HTTPStatus.NOT_FOUND, f'Storage {storage_id} not found')


@api.route('/search')
class ItemsSearch(Resource):
    @api.doc('search_items')
    @api.expect(ItemsModels.search_items)
    @api.response(200, 'Search completed', [ItemsModels.item_public])
    @api.response(400, 'Bad request')
    def get(self):
        """Search items by name and description"""
        args = ItemsModels.search_items.parse_args()
        content = args.content
        like_content = f'%{content}%'
        filters = [column.like(like_content) for column in [Items.name_ru, Items.name_en, Items.desc_ru, Items.desc_en]]
        res_search = [Items.orm2dict(item) for item in Items.query.filter(or_(*filters)).order_by(Items.item_id).all()]
        res = []
        for item in res_search:
            storage = Storages.get_storage_by_id(item['storage_id'])
            user = Users.get_user_by_id(storage['user_id'])
            united = OrderedDict([('owner', user)])
            united.update(get_object_with_additional_fields(item, Items))
            res.append(marshal(united, ItemsModels.item_public))
        return res
