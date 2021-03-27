from collections import OrderedDict
from flask_restplus import marshal, Resource
from http import HTTPStatus

from ..models import Items, Requests, Storages, Users
from ..models.enums import EnumRequestStatus
from ..utils.auth import check_admin, get_user_from_request, token_required
from ..utils.swagger import delete_object_by_id
from ..utils.swagger_models import RequestsModels, UsersModels


api = RequestsModels.api


@api.route('')
@api.doc(security='access-token')
class RequestsApi(Resource):
    @api.doc('get_requests')
    @api.response(200, 'Success', [RequestsModels.request])
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @token_required
    def get(self):
        """Get all requests"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        return Requests.get_requests()

    @api.doc('create_request')
    @api.expect(RequestsModels.create_request, validate=True)
    @api.response(201, 'Request created', RequestsModels.request)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @token_required
    def post(self):
        """Create new request"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        data = marshal(api.payload, RequestsModels.create_request, skip_none=True)
        request = Requests.create(data)
        if request is not None:
            return request, 201
        api.abort(HTTPStatus.BAD_REQUEST, 'Incorrect data for request creating supplied')

    @api.doc('update_request')
    @api.expect(RequestsModels.update_request, validate=True)
    @api.response(200, 'Request updated', RequestsModels.request)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def put(self):
        """Update request"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        data = marshal(api.payload, RequestsModels.update_request, skip_none=True)
        request = Requests.update(data)
        if request is not None:
            return request
        api.abort(HTTPStatus.NOT_FOUND, f'Request {data["request_id"]} not found')


@api.route('/<int:request_id>')
@api.doc(security='access-token')
class RequestsByIdApi(Resource):
    @api.doc('delete_request_by_id')
    @api.response(204, 'Request deleted')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def delete(self, request_id: int):
        """Delete request by id"""
        return delete_object_by_id(api, Requests, request_id)


def _get_own_request_response(request: dict) -> dict:
    item = Items.get_item_by_id(request['item_id'])
    storage = Storages.get_storage_by_id(item['storage_id'])
    owner = Users.get_user_by_id(storage['user_id'])
    if request['is_in_lending']:
        united_item = OrderedDict([('owner', marshal(owner, UsersModels.user_with_contacts))])
    else:
        united_item = OrderedDict([('owner', marshal(owner, UsersModels.user_public))])
    united_item.update(item)
    united_request = OrderedDict([('item', united_item)])
    united_request.update(request)
    return marshal(united_request, RequestsModels.request_me)


@api.route('/me')
@api.doc(security='access-token')
class RequestsMeApi(Resource):
    @api.doc('get_requests_me')
    @api.response(200, 'Success', [RequestsModels.request_me])
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def get(self):
        """Get own requests"""
        user = get_user_from_request(api)
        return list(map(_get_own_request_response, Requests.get_requests_by_user(user['user_id'])))

    @api.doc('create_request_me')
    @api.expect(RequestsModels.create_request_me, validate=True)
    @api.response(201, 'Request created', RequestsModels.request)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @token_required
    def post(self):
        """Create new request"""
        requester = get_user_from_request(api)
        data = marshal(api.payload, RequestsModels.create_request_me, skip_none=True)
        data['user_id'] = requester['user_id']
        request = Requests.create(data)
        if request is not None:
            return request, 201
        api.abort(HTTPStatus.BAD_REQUEST, 'Incorrect data for request creating supplied')

    @api.doc('update_request_me')
    @api.expect(RequestsModels.update_request_me, validate=True)
    @api.response(200, 'Request updated', RequestsModels.request)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def put(self):
        """Update request"""
        requester = get_user_from_request(api)
        data = marshal(api.payload, RequestsModels.update_request_me, skip_none=True)
        request = Requests.get_request_by_id(data['request_id'])
        if request is not None:
            if data['status'] in [EnumRequestStatus.CANCELED.name]:
                if request['user_id'] == requester['user_id']:
                    request = Requests.update(data)
                else:
                    api.abort(HTTPStatus.FORBIDDEN, f'Request {data["request_id"]} is not yours')
            else:
                item = Items.get_item_by_id(request['item_id'])
                storage = Storages.get_storage_by_id(item['storage_id'])
                if storage['user_id'] == requester['user_id']:
                    request = Requests.update(data)
                else:
                    api.abort(HTTPStatus.FORBIDDEN, f'Item {item["item_id"]} is not yours')
            if request['status'] == data['status']:
                return request
            api.abort(HTTPStatus.BAD_REQUEST, 'Incorrect status supplied')
        api.abort(HTTPStatus.NOT_FOUND, f'Request {data["request_id"]} not found')


@api.route('/me/<int:request_id>')
@api.doc(security='access-token')
class RequestsMeByIdApi(Resource):
    @api.doc('get_request_me_by_id')
    @api.response(200, 'Success', RequestsModels.request_me)
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def get(self, request_id: int):
        """Get own request by id"""
        requester = get_user_from_request(api)
        request = Requests.get_request_by_id(request_id)
        if request is not None:
            if request['user_id'] == requester['user_id']:
                return _get_own_request_response(request)
            api.abort(HTTPStatus.FORBIDDEN, f'Request {request_id} is not yours')
        api.abort(HTTPStatus.NOT_FOUND, f'Request {request_id} not found')


def _get_own_item_request_response(request: dict, item: dict) -> dict:
    user = Users.get_user_by_id(request['user_id'])
    if request['is_in_lending']:
        united = OrderedDict([('requester', marshal(user, UsersModels.user_with_contacts))])
    else:
        united = OrderedDict([('requester', marshal(user, UsersModels.user_public))])
    united['item'] = item
    united.update(request)
    return marshal(united, RequestsModels.request_item)


@api.route('/me/item/<int:item_id>')
@api.doc(security='access-token')
class RequestsMeByItemApi(Resource):
    @api.doc('get_requests_me_by_item')
    @api.response(200, 'Success', [RequestsModels.request_item])
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def get(self, item_id: int):
        """Get requests by own item"""
        requester = get_user_from_request(api)
        item = Items.get_item_by_id(item_id)
        if item is not None:
            storage = Storages.get_storage_by_id(item['storage_id'])
            if storage['user_id'] == requester['user_id']:
                return list(map(lambda request: _get_own_item_request_response(request, item),
                                Requests.get_requests_by_item(item_id)))
            api.abort(HTTPStatus.FORBIDDEN, f'Item {item_id} is not yours')
        api.abort(HTTPStatus.NOT_FOUND, f'Item {item_id} not found')


@api.route('/me/item/<int:item_id>/request/<int:request_id>')
@api.doc(security='access-token')
class RequestsMeByItemByIdApi(Resource):
    @api.doc('get_request_me_by_item_by_id')
    @api.response(200, 'Success', RequestsModels.request_item)
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def get(self, item_id: int, request_id: int):
        """Get request by own item and id"""
        requester = get_user_from_request(api)
        item = Items.get_item_by_id(item_id)
        if item is not None:
            request = Requests.get_request_by_id(request_id)
            if request is not None:
                if request['item_id'] == item_id:
                    storage = Storages.get_storage_by_id(item['storage_id'])
                    if storage['user_id'] == requester['user_id']:
                        return _get_own_item_request_response(request, item)
                    api.abort(HTTPStatus.FORBIDDEN, f'Item {item_id} is not yours')
                api.abort(HTTPStatus.BAD_REQUEST, f'Incorrect identifiers supplied')
            api.abort(HTTPStatus.NOT_FOUND, f'Request {request_id} not found')
        api.abort(HTTPStatus.NOT_FOUND, f'Item {item_id} not found')
