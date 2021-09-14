from contextlib import contextmanager
from datetime import datetime, timedelta
from sqlalchemy import Column, Sequence
from sqlalchemy.orm import Session
from typing import Any, Dict, List

from ..db import DeclarativeBase
from ...exceptions import DeletionError, ModelNotFoundError
from ...utils import any_in


DictStrAny = Dict[str, Any]


class Base(DeclarativeBase):
    __abstract__ = True

    seq = Sequence('ilis_seq')

    additional_fields = {}

    fields_to_update: List[Column] = []
    simple_fields_to_update: List[Column] = []

    @classmethod
    def _check_create(cls, data: DictStrAny, db: Session):
        pass

    @classmethod
    def check_exist(cls, obj_id: int, db: Session) -> 'Base':
        obj = cls.get_obj_by_id(obj_id, db)
        if obj is None:
            raise ModelNotFoundError(f'{cls.__name__[:-1]} {obj_id} not found')
        return obj

    @classmethod
    def _create_from_dict(cls, data: DictStrAny) -> 'Base':
        obj = cls()
        return obj._update_fields(data, cls.get_columns())

    @classmethod
    def _need_to_update(cls, data: DictStrAny) -> bool:
        return any_in([field.name for field in cls.fields_to_update], data)

    @classmethod
    def create(cls, data: DictStrAny, db: Session) -> 'Base':
        cls._check_create(data, db)
        obj = cls._create_from_dict(data)._add(db)
        obj._after_create()
        return obj

    @classmethod
    def delete(cls, obj_id: int, db: Session) -> 'Base':
        obj = cls.check_exist(obj_id, db)
        if obj.can_delete():
            obj._delete(db)
        else:
            raise DeletionError(f"{cls.__name__[:-1]} {obj_id} can't be deleted")
        return obj

    @classmethod
    def get_columns(cls) -> List[Column]:
        return list(cls.__table__.columns.values())

    @classmethod
    def get_id_name(cls) -> str:
        return cls.__table__.columns.keys()[0]

    @classmethod
    def get_obj_by_id(cls, obj_id: int, db: Session) -> 'Base':
        pass

    @classmethod
    def init(cls, db: Session):
        pass

    @classmethod
    def now(cls) -> datetime:
        return datetime.utcnow() + timedelta(hours=3)

    @classmethod
    def update(cls, data: DictStrAny, db: Session) -> 'Base':
        obj = cls.check_exist(data[cls.get_id_name()], db)
        obj = obj._update_fields(data, cls.simple_fields_to_update)._update_complicated_fields(data, db)._add(db)
        obj._after_update()
        return obj

    def _add(self, db: Session) -> 'Base':
        with self.auto_commit(db):
            db.add(self)
        return self

    def _after_create(self):
        pass

    def _after_delete(self):
        pass

    def _after_update(self):
        pass

    def _delete(self, db: Session):
        self._delete_self(db)
        self._after_delete()

    def _delete_self(self, db: Session) -> 'Base':
        with self.auto_commit(db, False):
            db.delete(self)
        return self

    def _update_complicated_fields(self, data: DictStrAny, db: Session) -> 'Base':
        return self

    def _update_fields(self, data: DictStrAny, fields: List[Column]) -> 'Base':
        for field in fields:
            if field.name in data and ((data[field.name] is None and field.nullable) or data[field.name] is not None):
                setattr(self, field.name, data[field.name])
        return self

    @contextmanager
    def auto_commit(self, db: Session, refresh: bool = True, throw: bool = True):
        try:
            yield
            db.commit()
            if refresh:
                db.refresh(self)
        except Exception as e:
            db.rollback()
            if throw:
                raise e

    def can_delete(self) -> bool:
        return True
