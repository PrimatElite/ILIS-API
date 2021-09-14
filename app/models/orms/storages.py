from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship, Session
from typing import List, Optional

from .base import Base, DictStrAny
from ...exceptions import UserNotFoundError
from ...utils import all_in


class Storages(Base):
    __tablename__ = 'storages'

    storage_id = Column(Integer, Base.seq, primary_key=True, server_default=Base.seq.next_value())
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    created_at = Column(DateTime, default=Base.now, nullable=False)
    updated_at = Column(DateTime, default=Base.now, onupdate=Base.now, nullable=False)

    user = relationship('Users', back_populates='storages')
    items = relationship('Items', back_populates='storage', cascade='all, delete')

    _location_fields_to_update: List[Column] = [latitude, longitude, address]
    simple_fields_to_update = [name]
    fields_to_update = simple_fields_to_update + _location_fields_to_update

    @classmethod
    def get_storage_by_id(cls, storage_id: int, db: Session) -> Optional['Storages']:
        return db.query(cls).filter_by(storage_id=storage_id).first()

    get_obj_by_id = get_storage_by_id

    @classmethod
    def get_storages(cls, db: Session) -> List['Storages']:
        return db.query(cls).order_by(cls.storage_id).all()

    @classmethod
    def get_storages_by_user(cls, user_id: int, db: Session) -> List['Storages']:
        return db.query(cls).filter_by(user_id=user_id).order_by(cls.storage_id).all()

    @classmethod
    def _check_create(cls, data: DictStrAny, db: Session):
        from .users import Users

        user = Users.get_user_by_id(data['user_id'], db)
        if user is None:
            raise UserNotFoundError(data['user_id'])

    def _update_complicated_fields(self, data: DictStrAny, db: Session) -> 'Storages':
        if all_in([field.name for field in self._location_fields_to_update], data):
            self._update_fields(data, self._location_fields_to_update)
        return self

    def can_delete(self) -> bool:
        return all(item.can_delete() for item in self.items)
