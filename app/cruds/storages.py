from sqlalchemy import Column
from typing import List

from .base import CRUDBase, DictStrAny, Session
from .users import CRUDUsers
from ..exceptions import UserNotFoundError
from ..models import ORMStorages
from ..utils import all_in


class CRUDStorages(CRUDBase):
    model = ORMStorages

    _location_fields_to_update: List[Column] = [ORMStorages.latitude, ORMStorages.longitude, ORMStorages.address]
    simple_fields_to_update = [ORMStorages.name]
    fields_to_update = simple_fields_to_update + _location_fields_to_update

    @classmethod
    def _check_creation(cls, db: Session, data: DictStrAny):
        user = CRUDUsers.get_by_id(db, data['user_id'])
        if user is None:
            raise UserNotFoundError(data['user_id'])

    @classmethod
    def _update_complicated_fields(cls, db: Session, obj: ORMStorages, data: DictStrAny) -> ORMStorages:
        if all_in([field.name for field in cls._location_fields_to_update], data):
            cls._update_fields(obj, data, cls._location_fields_to_update)
        return obj
