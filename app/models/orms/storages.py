from sqlalchemy import Column, Integer, String, Float
from typing import Union

from .base import Base
from ..db import seq
from ...utils import all_in


class Storages(Base):
    __tablename__ = 'storages'

    storage_id = Column(Integer, seq, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=False)

    location_fields_to_update = ['latitude', 'longitude', 'address']
    simple_fields_to_update = ['name']
    fields_to_update = simple_fields_to_update + location_fields_to_update

    @classmethod
    def get_storages(cls):
        return [cls.orm2dict(storage) for storage in cls.query.order_by(cls.storage_id).all()]

    @classmethod
    def get_storages_by_user(cls, user_id: int):
        return [cls.orm2dict(storage)
                for storage in cls.query.filter_by(user_id=user_id).order_by(cls.storage_id).all()]

    @classmethod
    def get_storage_by_id(cls, storage_id: int):
        return cls.orm2dict(cls.query.filter_by(storage_id=storage_id).first())

    get_obj_by_id = get_storage_by_id

    @classmethod
    def create(cls, data: dict) -> Union[dict, None]:
        from .users import Users

        user = Users.get_user_by_id(data['user_id'])
        if user is not None:
            storage = cls.dict2cls(data, False).add()
            storage_dict = cls.orm2dict(storage)
            return storage_dict
        return None

    @classmethod
    def update(cls, data: dict) -> Union[dict, None]:
        storage_dict = cls.get_storage_by_id(data['storage_id'])
        if storage_dict is not None:
            if not cls._need_to_update(data):
                return storage_dict
            storage = cls.dict2cls(storage_dict)._update_fields(data, cls.simple_fields_to_update)
            if all_in(cls.location_fields_to_update, data):
                storage._update_fields(data, cls.location_fields_to_update)
            storage.add()
            storage_dict = cls.orm2dict(storage)
        return storage_dict

    @classmethod
    def delete_storages_by_user(cls, user_id: int):
        for storage_dict in cls.get_storages_by_user(user_id):
            cls._delete(storage_dict)
