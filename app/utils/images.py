import os

from flask_restplus import Namespace
from flask import current_app
from http import HTTPStatus
from werkzeug import FileStorage
from werkzeug.utils import secure_filename


def get_file_dest(api: Namespace, file: FileStorage, time: str) -> str:
    destination = None
    for file_type in current_app.config.get('IMAGES_TYPES'):
        arg_type = 'image/' + file_type
        if file.mimetype == arg_type:
            destination = current_app.config.get('IMAGES_DIR')
            if not os.path.exists(destination):
                os.makedirs(destination)
    if destination is None:
        api.abort(HTTPStatus.FORBIDDEN, 'Use png or jpeg')
    file = '%s%s' % (destination, time + '-' + secure_filename(file.filename))
    return file
