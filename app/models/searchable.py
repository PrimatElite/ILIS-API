from sqlalchemy import case, event
from sqlalchemy.orm import Session
from typing import List

from .db import DeclarativeBase, SessionLocal
from .orms.base import Base
from ..search import elasticsearch


class Searchable(DeclarativeBase):
    __abstract__ = True
    __searchable__ = []

    @classmethod
    def search(cls, query: str, db: Session) -> List[Base]:
        ids = query_index(cls.__tablename__, query)
        if len(ids) > 0:
            id_name = cls.get_id_name()
            id_column = getattr(cls, id_name)
            when = [(id_, i) for i, id_ in enumerate(ids)]
            return db.query(cls).filter(id_column.in_(ids)).order_by(case(when, value=id_column)).all()
        return []

    @classmethod
    def before_commit(cls, session: Session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session: Session):
        for obj in session._changes['add']:
            if isinstance(obj, Searchable):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, Searchable):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, Searchable):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls, db: Session):
        for obj in db.query(cls):
            add_to_index(obj.__tablename__, obj)


def query_index(index: str, query: str) -> List[int]:
    search = elasticsearch.search(index=index, body={'query': {'multi_match': {'query': query, 'fields': ['*']}}})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids


def add_to_index(index: str, model: Searchable):
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    elasticsearch.index(index=index, id=getattr(model, f'{index[:-1]}_id'), body=payload)


def remove_from_index(index: str, model: Searchable):
    elasticsearch.delete(index=index, id=getattr(model, f'{index[:-1]}_id'))


event.listen(SessionLocal, 'before_commit', Searchable.before_commit)
event.listen(SessionLocal, 'after_commit', Searchable.after_commit)
