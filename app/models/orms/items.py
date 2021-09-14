from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Session
from typing import List, Optional

from .base import Base, DictStrAny
# TODO import Images
# from .images import Images
from .users import Users
from ...exceptions import StorageNotFoundError
from ...models.searchable import Searchable


class Items(Base, Searchable):
    __tablename__ = 'items'
    __searchable__ = ['name_ru', 'name_en', 'desc_ru', 'desc_en']

    item_id = Column(Integer, Base.seq, primary_key=True, server_default=Base.seq.next_value())
    storage_id = Column(Integer, ForeignKey('storages.storage_id'), nullable=False)
    name_ru = Column(String(length=127), nullable=False)
    name_en = Column(String(length=127), nullable=False)
    desc_ru = Column(String(length=511), nullable=False)
    desc_en = Column(String(length=511), nullable=False)
    count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=Base.now, nullable=False)
    updated_at = Column(DateTime, default=Base.now, onupdate=Base.now, nullable=False)

    storage = relationship('Storages', back_populates='items')
    requests = relationship('Requests', back_populates='item', cascade='all, delete')

    fields_to_update = [storage_id, name_ru, name_en, desc_ru, desc_en, count]
    simple_fields_to_update = [name_ru, name_en, desc_ru, desc_en]

    @property
    def owner(self) -> Users:
        return self.storage.user

    @property
    def remaining_count(self) -> int:
        requests_filter = filter(lambda r: r.is_in_lending, self.requests)
        lending_count = sum(map(lambda r: r.count, requests_filter))
        return self.count - lending_count

    @classmethod
    def get_item_by_id(cls, item_id: int, db: Session) -> Optional['Items']:
        return db.query(cls).filter_by(item_id=item_id).first()

    get_obj_by_id = get_item_by_id

    @classmethod
    def get_items(cls, db: Session) -> List['Items']:
        return db.query(cls).order_by(cls.item_id).all()

    @classmethod
    def get_items_by_storage(cls, storage_id: int, db: Session) -> List['Items']:
        return db.query(cls).filter_by(storage_id=storage_id).order_by(cls.item_id).all()

    @classmethod
    def get_remaining_count(cls, item: 'Items') -> int:
        requests_filter = filter(lambda r: r.is_in_lending, item.requests)
        lending_count = sum(map(lambda r: r.count, requests_filter))
        return item.count - lending_count

    @classmethod
    def _check_create(cls, data: DictStrAny, db: Session):
        from .storages import Storages

        storage = Storages.get_storage_by_id(data['storage_id'], db)
        if storage is None:
            raise StorageNotFoundError(data['storage_id'])

    def _update_complicated_fields(self, data: DictStrAny, db: Session) -> 'Items':
        from .storages import Storages

        if data['storage_id'] is not None:
            dest_storage = Storages.get_storage_by_id(data['storage_id'], db)
            if dest_storage is not None and self.storage.user_id == dest_storage.user_id:
                self.storage_id = data['storage_id']
        if data['count'] is not None and data['count'] >= self.count - self.remaining_count:
            self.count = data['count']
        return self

    def can_delete(self) -> bool:
        return all(request.can_delete() for request in self.requests)
