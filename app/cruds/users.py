from typing import Optional, Union

from .base import CRUDBase, DictStrAny, Session
from ..exceptions import UserExistingError
from ..models import EnumLoginService, EnumUserRole, ORMUsers
from ..utils import get_db_initialization


class CRUDUsers(CRUDBase):
    model = ORMUsers

    fields_to_update = [ORMUsers.name, ORMUsers.surname, ORMUsers.role, ORMUsers.email, ORMUsers.phone, ORMUsers.avatar]
    simple_fields_to_update = fields_to_update

    @classmethod
    def get_user_by_login(cls, db: Session, login_id: str,
                          login_type: Union[str, EnumLoginService]) -> Optional[ORMUsers]:
        return db.query(cls.model).filter_by(login_id=login_id, login_type=login_type).first()

    @classmethod
    def _check_creation(cls, db: Session, data: DictStrAny):
        user = cls.get_user_by_login(db, data['login_id'], data['login_type'])
        if user is not None:
            raise UserExistingError(data['login_id'], data['login_type'])

    @classmethod
    def init(cls, db: Session):
        admins = get_db_initialization()['admins']
        for admin in admins:
            if cls.get_user_by_login(db, admin['login_id'], admin['login_type']) is None:
                admin['role'] = EnumUserRole.ADMIN
                cls.create(db, admin)
