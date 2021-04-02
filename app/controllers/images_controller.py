import os

from flask import current_app
from flask_restplus import marshal, Resource
from http import HTTPStatus
from flask.views import View

from werkzeug.utils import secure_filename

from ..models import Images, Items
from ..utils.auth import check_admin, get_user_from_request, token_required
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


@api.route('/item/<int:item_id>/upload_image')
@api.doc(security='access-token')
class ImagesApi(Resource):
    @api.doc('create_image')
    @api.expect(ImagesModels.file_upload)
    @api.response(201, 'Image created', ImagesModels.image)
    @api.response(400, 'Bad request')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Not found')
    @token_required
    def post(self, item_id: int):
        """Create new image"""
        requester = get_user_from_request(api)
        check_admin(api, requester)
        args = ImagesModels.file_upload.parse_args()
        destination = None
        for file_type in current_app.config.get('IMAGES_TYPES'):
            arg_type = 'image/' + file_type
            if args['image'].mimetype == arg_type:
                destination = current_app.config.get('IMAGES_DIR')
                if not os.path.exists(destination):
                    os.makedirs(destination)
        if destination is None:
            api.abort(HTTPStatus.FORBIDDEN, 'Use png or jpeg')
        file = '%s%s' % (destination, args['image'].filename)# + Images.now().replace(microsecond=0).isoformat())
        args['image'].save(file)
        data = marshal(api.payload, ImagesModels.create_image, skip_none=True)
        data['item_id'] = item_id
        data['path'] = file
        item = Items.get_item_by_id(data['item_id'])
        if item is not None:
            image = Images.create(data)
            return image, 201
