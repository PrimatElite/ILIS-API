from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from .base import ORMBase


class ORMStorages(ORMBase):
    __tablename__ = 'storages'

    storage_id = Column(Integer, ORMBase.seq, primary_key=True, server_default=ORMBase.seq.next_value())
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    created_at = Column(DateTime, default=ORMBase.now, nullable=False)
    updated_at = Column(DateTime, default=ORMBase.now, onupdate=ORMBase.now, nullable=False)

    owner = relationship('ORMUsers', back_populates='storages')
    items = relationship('ORMItems', back_populates='storage', cascade='all, delete')

    def can_delete(self) -> bool:
        return all(item.can_delete() for item in self.items)
