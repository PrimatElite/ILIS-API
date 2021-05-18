from sqlalchemy import Column, DateTime, Integer, String
from typing import List, Optional

from .base import Base
# TODO import Images
# from .images import Images
from .requests import Requests
from ..db import seq
from ...cache import cache
from ...models.searchable import Searchable


class Items(Base, Searchable):
    __tablename__ = 'items'
    __searchable__ = ['name_ru', 'name_en', 'desc_ru', 'desc_en']

    item_id = Column(Integer, seq, primary_key=True)
    storage_id = Column(Integer, nullable=False)
    name_ru = Column(String(length=127), nullable=False)
    name_en = Column(String(length=127), nullable=False)
    desc_ru = Column(String(length=511), nullable=False)
    desc_en = Column(String(length=511), nullable=False)
    count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=Base.now)
    updated_at = Column(DateTime, default=Base.now, onupdate=Base.now)

    additional_fields = {
        'remaining_count': lambda item_id: Items.get_remaining_count(Items.get_item_by_id(item_id))
    }

    fields_to_update = ['storage_id', 'name_ru', 'name_en', 'desc_ru', 'desc_en', 'count']
    simple_fields_to_update = ['name_ru', 'name_en', 'desc_ru', 'desc_en']

    # TODO add image deleter link in item
    delete_relation_funcs = [Requests.delete_requests_by_item]

    @classmethod
    @cache.cache_list('get_items', field='item_id')
    def get_items(cls) -> List[dict]:
        return [cls.orm2dict(item) for item in cls.query.order_by(cls.item_id).all()]

    @classmethod
    @cache.cache_list('get_items_by_storage', field='item_id')
    def get_items_by_storage(cls, storage_id: int) -> List[dict]:
        return [cls.orm2dict(item) for item in cls.query.filter_by(storage_id=storage_id).order_by(cls.item_id).all()]

    @classmethod
    @cache.cache_element('get_item_by_id')
    def get_item_by_id(cls, item_id: int) -> Optional[dict]:
        return cls.orm2dict(cls.query.filter_by(item_id=item_id).first())

    get_obj_by_id = get_item_by_id

    @classmethod
    def get_remaining_count(cls, item_dict: dict) -> int:
        requests_filter = filter(lambda r: r['is_in_lending'], Requests.get_requests_by_item(item_dict['item_id']))
        lending_count = sum(map(lambda r: r['count'], requests_filter))
        return item_dict['count'] - lending_count

    @classmethod
    def create(cls, data: dict) -> Optional[dict]:
        from .storages import Storages

        storage_dict = Storages.get_storage_by_id(data['storage_id'])
        if storage_dict is not None:
            item = cls.dict2cls(data, False).add()
            item_dict = cls.orm2dict(item)
            cls.after_create(item_dict)
            return item_dict
        return None

    @classmethod
    def update(cls, data: dict) -> Optional[dict]:
        from .storages import Storages

        item_dict = cls.get_item_by_id(data['item_id'])
        if item_dict is not None:
            if not cls._need_to_update(data):
                return item_dict
            item = cls.dict2cls(item_dict)._update_fields(data, cls.simple_fields_to_update)
            if 'storage_id' in data:
                start_storage = Storages.get_storage_by_id(item_dict['storage_id'])
                dest_storage = Storages.get_storage_by_id(data['storage_id'])
                if dest_storage is not None and start_storage['user_id'] == dest_storage['user_id']:
                    item = item._update_fields(data, ['storage_id'])
            if 'count' in data and data['count'] >= item.count - cls.get_remaining_count(item_dict):
                item = item._update_fields(data, ['count'])
            item = item.add()
            item_dict = cls.orm2dict(item)
            cls.after_update(item_dict)
        return item_dict

    @classmethod
    def can_delete(cls, item_dict: dict) -> bool:
        return all(Requests.can_delete(request_dict)
                   for request_dict in Requests.get_requests_by_item(item_dict['item_id']))

    @classmethod
    def delete_items_by_storage(cls, storage_id: int):
        for item_dict in cls.get_items_by_storage(storage_id):
            cls._delete(item_dict)


Items.__cached__ = [Items.get_items, Items.get_items_by_storage, Items.get_item_by_id]
