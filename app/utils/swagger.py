from flask_restplus import Namespace
from http import HTTPStatus
from typing import List, Optional, Type

from ..models.orms.base import Base
from ..utils.auth import check_admin, get_user_from_request


def delete_object_by_id(api: Namespace, object_class: Type[Base], object_id: int):
    requester = get_user_from_request(api)
    check_admin(api, requester)
    ret = object_class.delete(object_id)
    if ret is not None:
        if ret:
            return '', 204
        api.abort(HTTPStatus.FORBIDDEN, f'{object_class.__name__[:-1]} {object_id} can\'t be deleted')
    api.abort(HTTPStatus.NOT_FOUND, f'{object_class.__name__[:-1]} {object_id} not found')


def get_object_with_additional_fields(object_dict: dict, object_class: Type[Base],
                                      additional_fields: Optional[List[str]] = None) -> dict:
    additional_dict = object_class.get_additional_fields(object_dict[object_class.get_id_name()], additional_fields)
    object_dict.update(additional_dict)
    return object_dict


def get_objects_with_additional_fields(objects_list: List[dict], object_class: Type[Base],
                                       additional_fields: Optional[List[str]] = None) -> List[dict]:
    return list(map(lambda object_dict: get_object_with_additional_fields(object_dict, object_class, additional_fields),
                    objects_list))
