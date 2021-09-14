from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship, Session
from typing import List, Optional

from .base import Base, DictStrAny
from ..enums import EnumLoginService, EnumUserRole
from ...exceptions import UserExistingError
from ...utils import get_db_initialization


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, Base.seq, primary_key=True, server_default=Base.seq.next_value())
    login_id = Column(String, nullable=False)
    login_type = Column(Enum(EnumLoginService), nullable=False)
    name = Column(String, default='', nullable=False)
    surname = Column(String, default='', nullable=False)
    role = Column(Enum(EnumUserRole), default=EnumUserRole.USER, nullable=False)
    email = Column(String, default='', nullable=False)
    phone = Column(String, default='', nullable=False)
    avatar = Column(String, default='', nullable=False)
    created_at = Column(DateTime, default=Base.now, nullable=False)
    updated_at = Column(DateTime, default=Base.now, onupdate=Base.now, nullable=False)

    requests = relationship('Requests', back_populates='user', cascade='all, delete')
    storages = relationship('Storages', back_populates='user', cascade='all, delete')

    fields_to_update = [name, surname, role, email, phone, avatar]
    simple_fields_to_update = fields_to_update

    @classmethod
    def get_user_by_id(cls, user_id: int, db: Session) -> Optional['Users']:
        return db.query(cls).filter_by(user_id=user_id).first()

    get_obj_by_id = get_user_by_id

    @classmethod
    def get_users(cls, db: Session) -> List['Users']:
        return db.query(cls).order_by(cls.user_id).all()

    @classmethod
    def get_user_by_login(cls, login_id: str, login_type: str, db: Session) -> Optional['Users']:
        return db.query(cls).filter_by(login_id=login_id, login_type=login_type).first()

    @classmethod
    def _check_create(cls, data: DictStrAny, db: Session):
        user = cls.get_user_by_login(data['login_id'], data['login_type'], db)
        if user is not None:
            raise UserExistingError(data['login_id'], data['login_type'])

    def can_delete(self) -> bool:
        storages_condition = all(storage.can_delete() for storage in self.storages)
        if not storages_condition:
            return False
        return all(request.can_delete() for request in self.requests)

    @classmethod
    def init(cls, db: Session):
        admins = get_db_initialization()['admins']
        for admin in admins:
            if cls.get_user_by_login(admin['login_id'], admin['login_type'], db) is None:
                admin['role'] = EnumUserRole.ADMIN
                cls.create(admin, db)
