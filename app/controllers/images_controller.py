from flask_restplus import marshal, Resource
from http import HTTPStatus
from collections import OrderedDict

from ..models import Images, Items, Storages
from ..utils.auth import check_admin, get_user_from_request, token_required
from ..utils.images import get_file_dest
from ..utils.swagger import delete_object_by_id
from ..utils.swagger_models import ImagesModels


api = ImagesModels.api


@api.route('')
@api.doc(security='access-token')
class ImagesApi(Resource):
    @api.doc('get_images')
    @api.response(200, 'Success', [ImagesModels.image])
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @token_required
    def get(self):
        """Get all images"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        return Images.get_images()

    @api.doc('create_image')
    @api.expect(ImagesModels.file_upload)
    @api.response(201, 'Image created', ImagesModels.image)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def post(self):
        """Upload new image"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        args = ImagesModels.file_upload.parse_args()
        time = Images.now().replace(microsecond=0).isoformat()
        t = time.replace(':', '-')
        file = get_file_dest(api, args['image'], t)
        data = OrderedDict([])
        data['item_id'] = args['item_id']
        data['path'] = file
        image = Images.create(data)
        if image is not None:
            args['image'].save(file)
            return image, 201
        api.abort(HTTPStatus.NOT_FOUND, f'Item {data["item_id"]} not found')


@api.route('/<int:image_id>')
class ImageByIdApi(Resource):
    @api.doc('get_image_by_id')
    @api.response(200, 'Success', ImagesModels.image)
    @api.response(404, 'Not found')
    def get(self, image_id: int):
        """Get image by id"""
        image = Images.get_image_by_id(image_id)
        if image is not None:
            return image
        api.abort(HTTPStatus.NOT_FOUND, f'Image {image_id} not found')

    @api.doc('delete_item_by_id', security='access-token')
    @api.response(204, 'Item deleted')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def delete(self, image_id: int):
        """Delete item by id"""
        return delete_object_by_id(api, Images, image_id)


@api.route('/me')
@api.doc(security='access-token')
class ImagesMeApi(Resource):
    @api.doc('create_image_me')
    @api.expect(ImagesModels.file_upload, validate=True)
    @api.response(201, 'Item created', ImagesModels.image)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def post(self):
        """Create new item in own storage"""
        user = get_user_from_request(api)
        args = ImagesModels.file_upload.parse_args()
        time = Images.now().replace(microsecond=0).isoformat()
        t = time.replace(':', '-')
        file = get_file_dest(api, args['image'], t)
        data = OrderedDict([])
        data['item_id'] = args['item_id']
        data['path'] = file
        item = Items.get_item_by_id(data['item_id'])
        if item is not None:
            storage = Storages.get_storage_by_id(item['storage_id'])
            if user['user_id'] == storage['user_id']:
                image = Images.create(data)
                args['image'].save(file)
                return image, 201
            api.abort(HTTPStatus.FORBIDDEN, f'Item {data["item_id"]} is not yours')
        api.abort(HTTPStatus.NOT_FOUND, f'Item {data["item_id"]} not found')


@api.route('/item/<int:item_id>')
class ImagesMeByItemIdApi(Resource):
    @api.doc('get_images_by_item')
    @api.response(200, 'Success', [ImagesModels.image])
    @api.response(404, 'Not found')
    def get(self, item_id: int):
        """Get images of item"""
        item = Items.get_item_by_id(item_id)
        if item is not None:
            images = Images.get_images_by_item(item_id)
            return images
        api.abort(HTTPStatus.NOT_FOUND, f'Item {item_id} not found')
