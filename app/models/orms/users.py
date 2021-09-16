from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship

from .base import ORMBase
from ..enums import EnumLoginService, EnumUserRole


class ORMUsers(ORMBase):
    __tablename__ = 'users'

    user_id = Column(Integer, ORMBase.seq, primary_key=True, server_default=ORMBase.seq.next_value())
    login_id = Column(String, nullable=False)
    login_type = Column(Enum(EnumLoginService), nullable=False)
    name = Column(String, default='', nullable=False)
    surname = Column(String, default='', nullable=False)
    role = Column(Enum(EnumUserRole), default=EnumUserRole.USER, nullable=False)
    email = Column(String, default='', nullable=False)
    phone = Column(String, default='', nullable=False)
    avatar = Column(String, default='', nullable=False)
    created_at = Column(DateTime, default=ORMBase.now, nullable=False)
    updated_at = Column(DateTime, default=ORMBase.now, onupdate=ORMBase.now, nullable=False)

    requests = relationship('ORMRequests', back_populates='requester', cascade='all, delete')
    storages = relationship('ORMStorages', back_populates='owner', cascade='all, delete')

    def can_delete(self) -> bool:
        storages_condition = all(storage.can_delete() for storage in self.storages)
        if not storages_condition:
            return False
        return all(request.can_delete() for request in self.requests)
