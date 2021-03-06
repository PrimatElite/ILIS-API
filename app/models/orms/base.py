from collections import OrderedDict
from datetime import datetime, timedelta
from dateutil import parser
from enum import Enum
from typing import List, Union

from ...utils import any_in, datetime2str, validate_iso8601
from app.models.db import db


class Base(db.Model):
    __abstract__ = True

    additional_fields = {}

    fields_to_update = []
    simple_fields_to_update = []

    delete_relation_funcs = []

    @classmethod
    def now(cls) -> datetime:
        return datetime.utcnow() + timedelta(hours=3)

    @classmethod
    def get_obj_by_id(cls, obj_id: int) -> 'Base':
        pass

    @classmethod
    def get_id_name(cls) -> str:
        return cls.__table__.columns.keys()[0]

    @classmethod
    def get_columns_names(cls) -> List[str]:
        return list(cls.__table__.columns.keys())

    @classmethod
    def get_additional_fields(cls, obj_id: int, fields: List[str] = None) -> dict:
        result = OrderedDict([(cls.get_id_name(), obj_id)])
        if fields is None:
            fields = cls.additional_fields.keys()
        for field, func in cls.additional_fields.items():
            if field in fields:
                result.update({field: func(obj_id)})
        return result

    @classmethod
    def orm2dict(cls, obj: Union['Base', None], fields: List[str] = None) -> Union[dict, None]:
        def dictionate_entity(entity):
            if isinstance(entity, datetime):
                return datetime2str(entity)
            elif isinstance(entity, Enum):
                return entity.name
            else:
                return entity

        if obj is None:
            return None
        columns = cls.get_columns_names()
        if fields is None:
            fields = columns
        return OrderedDict([(field, dictionate_entity(getattr(obj, field))) for field in fields if field in columns])

    @classmethod
    def dict2cls(cls, data: dict, merge: bool = True) -> 'Base':
        obj = cls()
        obj._update_fields(data, cls.get_columns_names())
        if merge:
            return db.session.merge(obj)
        return obj

    def _update_fields(self, data: dict, fields: list) -> 'Base':
        for field in fields:
            if field in data:
                field_type = self.__table__.columns[field].type.python_type
                if field_type == datetime:
                    if validate_iso8601(data[field]):
                        setattr(self, field, parser.parse(data[field]))
                elif issubclass(field_type, Enum):
                    setattr(self, field, field_type[data[field]])
                else:
                    setattr(self, field, data[field])
        return self

    @classmethod
    def _need_to_update(cls, data: dict) -> bool:
        return any_in(cls.fields_to_update, data)

    def add(self) -> 'Base':
        with db.auto_commit():
            db.session.add(self)
        return self

    def delete_self(self) -> 'Base':
        with db.auto_commit():
            db.session.delete(self)
        return self

    def _before_deletion(self):
        pass

    @classmethod
    def delete(cls, obj_id: int) -> Union['Base', None]:
        obj_dict = cls.get_obj_by_id(obj_id)
        if obj_dict:
            obj = cls.dict2cls(obj_dict)
            obj._before_deletion()
            obj_id = getattr(obj, cls.get_id_name())
            for delete_func in cls.delete_relation_funcs:
                delete_func(obj_id)
            obj.delete_self()
            return obj_dict
        return None
