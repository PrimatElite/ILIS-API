import os

from flask_restplus import Namespace
from flask import current_app
from typing import Optional
from werkzeug import FileStorage
from werkzeug.utils import secure_filename


def get_file_dest(file: FileStorage, additional_info: str) -> Optional[str]:
    destination = None
    for file_type in current_app.config.get('IMAGES_TYPES'):
        arg_type = 'image/' + file_type
        if file.mimetype == arg_type:
            destination = current_app.config.get('IMAGES_DIR')
            if not os.path.exists(destination):
                os.makedirs(destination)
    if destination is not None:
        return '%s%s' % (destination, additional_info + '_' + secure_filename(file.filename))
    return None
