from sqlalchemy import Column, DateTime, Enum, event, Integer, String, Table
from sqlalchemy.engine import Connection
from typing import List, Optional

from .base import Base
from .requests import Requests
from .storages import Storages
from ..db import seq
from ..enums import EnumLoginService, EnumUserRole
from ...cache import cache
from ...utils import get_db_initialization


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, seq, primary_key=True)
    login_id = Column(String, nullable=False)
    login_type = Column(Enum(EnumLoginService), nullable=False)
    name = Column(String)
    surname = Column(String)
    role = Column(Enum(EnumUserRole), nullable=False)
    email = Column(String)
    phone = Column(String)
    avatar = Column(String)
    created_at = Column(DateTime, default=Base.now)
    updated_at = Column(DateTime, default=Base.now, onupdate=Base.now)

    fields_to_update = ['name', 'surname', 'role', 'email', 'phone', 'avatar']
    simple_fields_to_update = fields_to_update

    delete_relation_funcs = [Storages.delete_storages_by_user]

    @classmethod
    @cache.cache_list('get_users', field='user_id')
    def get_users(cls) -> List[dict]:
        return [cls.orm2dict(user) for user in cls.query.order_by(cls.user_id).all()]

    @classmethod
    @cache.cache_element('get_user_by_id')
    def get_user_by_id(cls, user_id: int) -> Optional[dict]:
        return cls.orm2dict(cls.query.filter_by(user_id=user_id).first())

    get_obj_by_id = get_user_by_id

    @classmethod
    @cache.cache_element('get_user_by_login')
    def get_user_by_login(cls, login_id: str, login_type: str) -> Optional[dict]:
        return cls.orm2dict(cls.query.filter_by(login_id=login_id, login_type=login_type).first())

    @classmethod
    def create(cls, data: dict) -> dict:
        user_dict = cls.get_user_by_login(data['login_id'], data['login_type'])
        if user_dict is None:
            user = cls.dict2cls(data, False).add()
            user_dict = cls.orm2dict(user)
            cls.after_create(user_dict)
        return user_dict

    @classmethod
    def update(cls, data: dict) -> Optional[dict]:
        user_dict = cls.get_user_by_id(data['user_id'])
        if user_dict is not None:
            if not cls._need_to_update(data):
                return user_dict
            user = cls.dict2cls(user_dict)._update_fields(data, cls.simple_fields_to_update).add()
            user_dict = cls.orm2dict(user)
            cls.after_update(user_dict)
        return user_dict

    @classmethod
    def can_delete(cls, user_dict: dict) -> bool:
        storages_condition = all(Storages.can_delete(storage_dict)
                                 for storage_dict in Storages.get_storages_by_user(user_dict['user_id']))
        if not storages_condition:
            return False
        return all(Requests.can_delete(request_dict)
                   for request_dict in Requests.get_requests_by_user(user_dict['user_id']))

    # Integration with Flask-Admin and Flask-Login:

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id


Users.__cached__ = [Users.get_users, Users.get_user_by_id, Users.get_user_by_login]


@event.listens_for(Users.__table__, 'after_create')
def create_all(target: Table, connection: Connection, **kwargs):
    admins = get_db_initialization()['admins']
    for admin in admins:
        admin['role'] = EnumUserRole.ADMIN.name
        connection.execute(Users.__table__.insert(), admin)
