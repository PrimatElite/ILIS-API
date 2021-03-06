from sqlalchemy import Column, DateTime, Enum, event, Integer, String
from typing import Union

from .base import Base
from ..db import seq
from ..enums import EnumLoginService, EnumUserRole
from ...utils import get_db_initialization


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, seq, primary_key=True)
    login_id = Column(Integer, nullable=False)
    login_type = Column(Enum(EnumLoginService), nullable=False)
    name = Column(String)
    surname = Column(String)
    role = Column(Enum(EnumUserRole), nullable=False)
    email = Column(String)
    phone = Column(String)
    avatar = Column(String)
    created_at = Column(DateTime, default=Base.now)
    updated_at = Column(DateTime, default=Base.now, onupdate=Base.now)

    fields_to_update = ['name', 'surname', 'role', 'email', 'phone']
    simple_fields_to_update = fields_to_update

    @classmethod
    def get_users(cls):
        return [cls.orm2dict(user) for user in cls.query.order_by(cls.user_id).all()]

    @classmethod
    def get_user_by_id(cls, user_id):
        return cls.orm2dict(cls.query.filter_by(user_id=user_id).first())

    get_item_by_id = get_user_by_id

    @classmethod
    def get_user_by_login(cls, login_id, login_type):
        return cls.orm2dict(cls.query.filter_by(login_id=login_id, login_type=login_type).first())

    @classmethod
    def create(cls, data: dict) -> dict:
        user_dict = cls.get_user_by_login(data['login_id'], data['login_type'])
        if not user_dict:
            user = cls.dict2cls(data, False).add()
            user_dict = cls.orm2dict(user)
        return user_dict

    @classmethod
    def update(cls, data: dict) -> Union[dict, None]:
        user_dict = cls.get_user_by_id(data['user_id'])
        if user_dict:
            if not cls._need_to_update(data):
                return user_dict
            user = cls.dict2cls(user_dict)._update_fields(user_dict, cls.simple_fields_to_update).add()
            user_dict = cls.orm2dict(user)
        return user_dict


@event.listens_for(Users.__table__, 'after_create')
def create_all(*args, **kwargs):
    admins = get_db_initialization()['admins']
    for admin in admins:
        admin['role'] = EnumUserRole.ADMIN
        Users.dict2cls(admin, False).add()
