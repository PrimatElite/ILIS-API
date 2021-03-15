from sqlalchemy import Column, DateTime, Integer, String
from typing import List, Optional

from .base import Base
from ..db import seq

# TODO import Requests and Images
#from .request import Requests
#from .images import Images

class Items(Base):
    __tablename__ = 'items'

    item_id = Column(Integer, seq, primary_key=True)
    storage_id = Column(Integer, nullable=False)
    name_ru = Column(String(length=127))
    name_en = Column(String(length=127))
    desc_ru = Column(String(length=511))
    desc_en = Column(String(length=511))
    count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=Base.now)
    updated_at = Column(DateTime, default=Base.now, onupdate=Base.now)

    fields_to_update = ['storage_id', 'name_ru', 'name_en', 'desc_ru', 'desc_en', 'count']
    simple_fields_to_update = ['storage_id', 'name_ru', 'name_en', 'desc_ru', 'desc_en']

    # TODO request and image deleter link in item
    # delete_relation_funcs = [Images.delete_images_by_item, Requests.delete_requests_by_item]

    @classmethod
    def get_items(cls) -> List[dict]:
        return [cls.orm2dict(item) for item in cls.query.order_by(cls.item_id).all()]

    @classmethod
    def get_items_by_storage(cls, storage_id: int) -> List[dict]:
        return [cls.orm2dict(item) for item in cls.query.filter_by(storage_id=storage_id).order_by(cls.item_id).all()]

    @classmethod
    def get_item_by_id(cls, item_id: int) -> Optional[dict]:
        return cls.orm2dict(cls.query.filter_by(item_id=item_id).first())

    get_obj_by_id = get_item_by_id

    @classmethod
    def create(cls, data: dict) -> Optional[dict]:
        from .storages import Storages

        storage_dict = Storages.get_storage_by_id(data['storage_id'])
        if storage_dict is not None:
            item = cls.dict2cls(data, False).add()
            item_dict = cls.orm2dict(item)
            return item_dict
        return None

    @classmethod
    def update(cls, data: dict) -> Optional[dict]:
        item_dict = cls.get_item_by_id(data['item_id'])
        if item_dict is not None:
            if not cls._need_to_update(data):
                return item_dict
            item = cls.dict2cls(item_dict)._update_fields(data, cls.simple_fields_to_update)
            # TODO check request based count on item update
            # requests_dict = Requests.get_requests_by_item_id(data['item_id'])
            # count = 0
            # for request_dict in requests_dict:
            #     count += request_dict['count']
            # if data['count'] < count:
            #     return None
            item = item._update_fields(data, ['count'])
            item = item.add()
            item_dict = cls.orm2dict(item)
            return item_dict
        return None

    @classmethod
    def delete_items_by_storage(cls, storage_id: int):
        for item_dict in cls.get_items_by_storage(storage_id):
            cls._delete(item_dict)
