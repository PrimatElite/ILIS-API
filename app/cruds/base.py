from contextlib import contextmanager
from sqlalchemy import Column
from sqlalchemy.orm import Session
from typing import Any, Dict, List

from ..exceptions import DeletionError, ModelNotFoundError
from ..models import ORMBase
from ..utils import any_in


DictStrAny = Dict[str, Any]


class CRUDBase:
    model = ORMBase

    fields_to_update: List[Column] = []
    simple_fields_to_update: List[Column] = []

    @classmethod
    def get_columns(cls) -> List[Column]:
        return list(cls.model.__table__.columns.values())

    @classmethod
    def get_id_name(cls) -> str:
        return cls.model.__table__.columns.keys()[0]

    @classmethod
    def get_id_column(cls) -> Column:
        return cls.model.__table__.columns.values()[0]

    @classmethod
    def get_by_id(cls, db: Session, object_id: int) -> ORMBase:
        return db.query(cls.model).filter_by(**{cls.get_id_name(): object_id}).first()

    @classmethod
    def get_list(cls, db: Session) -> List[ORMBase]:
        return db.query(cls.model).order_by(cls.get_id_column()).all()

    @classmethod
    def get_count(cls, db: Session) -> int:
        return db.query(cls.model).count()

    @classmethod
    @contextmanager
    def auto_commit(cls, db: Session, obj: ORMBase, refresh: bool = True, throw: bool = True):
        try:
            yield
            db.commit()
            if refresh:
                db.refresh(obj)
        except Exception as e:
            db.rollback()
            if throw:
                raise e

    @classmethod
    def _check_creation(cls, db: Session, data: DictStrAny):
        pass

    @classmethod
    def _update_fields(cls, obj: ORMBase, data: DictStrAny, fields: List[Column]) -> ORMBase:
        for field in fields:
            if field.name in data and ((data[field.name] is None and field.nullable) or data[field.name] is not None):
                setattr(obj, field.name, data[field.name])
        return obj

    @classmethod
    def _create_from_dict(cls, data: DictStrAny) -> ORMBase:
        obj = cls.model()
        return cls._update_fields(obj, data, cls.get_columns())

    @classmethod
    def _add_object(cls, db: Session, obj: ORMBase) -> ORMBase:
        with cls.auto_commit(db, obj):
            db.add(obj)
        return obj

    @classmethod
    def _after_create(cls, obj: ORMBase):
        pass

    @classmethod
    def create(cls, db: Session, data: DictStrAny) -> ORMBase:
        cls._check_creation(db, data)
        obj = cls._create_from_dict(data)
        obj = cls._add_object(db, obj)
        cls._after_create(obj)
        return obj

    @classmethod
    def check_existence(cls, db: Session, object_id: int) -> ORMBase:
        obj = cls.get_by_id(db, object_id)
        if obj is None:
            raise ModelNotFoundError(f'{cls.model.__name__[3:-1]} {object_id} not found')
        return obj

    @classmethod
    def _update_complicated_fields(cls, db: Session, obj: ORMBase, data: DictStrAny) -> ORMBase:
        return obj

    @classmethod
    def _need_to_update(cls, data: DictStrAny) -> bool:
        return any_in([field.name for field in cls.fields_to_update], data)

    @classmethod
    def _after_update(cls, obj: ORMBase):
        pass

    @classmethod
    def update(cls, db: Session, data: DictStrAny) -> ORMBase:
        obj = cls.check_existence(db, data[cls.get_id_name()])
        obj = cls._update_fields(obj, data, cls.simple_fields_to_update)
        obj = cls._update_complicated_fields(db, obj, data)
        obj = cls._add_object(db, obj)
        cls._after_update(obj)
        return obj

    @classmethod
    def _delete_object(cls, db: Session, obj: ORMBase) -> ORMBase:
        with cls.auto_commit(db, obj, False):
            db.delete(obj)
        return obj

    @classmethod
    def _after_delete(cls, obj: ORMBase):
        pass

    @classmethod
    def _delete(cls, db: Session, obj: ORMBase) -> ORMBase:
        obj = cls._delete_object(db, obj)
        cls._after_delete(obj)
        return obj

    @classmethod
    def delete(cls, db: Session, object_id: int) -> ORMBase:
        obj = cls.check_existence(db, object_id)
        if obj.can_delete():
            obj = cls._delete(db, obj)
        else:
            raise DeletionError(f"{cls.model.__name__[3:-1]} {object_id} can't be deleted")
        return obj

    @classmethod
    def init(cls, db: Session):
        pass
