from sqlalchemy import case, event
from typing import List

from .base import Base, Session
from ..models import ORMSearchable, SessionLocal
from ..search import elasticsearch


class Searchable(Base):
    @classmethod
    def search(cls, db: Session, query: str) -> List[ORMSearchable]:
        ids = query_index(cls.model.__tablename__, query)
        if len(ids) > 0:
            id_column = cls.get_id_column()
            when = [(id_, i) for i, id_ in enumerate(ids)]
            return db.query(cls.model).filter(id_column.in_(ids)).order_by(case(when, value=id_column)).all()
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
            if isinstance(obj, ORMSearchable):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, ORMSearchable):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, ORMSearchable):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls, db: Session):
        for obj in db.query(cls.model):
            add_to_index(obj.__tablename__, obj)


def query_index(index: str, query: str) -> List[int]:
    search = elasticsearch.search(index=index, body={'query': {'multi_match': {'query': query, 'fields': ['*']}}})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids


def add_to_index(index: str, obj: ORMSearchable):
    payload = {}
    for field in obj.__searchable__:
        payload[field.name] = getattr(obj, field.name)
    elasticsearch.index(index=index, id=getattr(obj, f'{index[:-1]}_id'), body=payload)


def remove_from_index(index: str, obj: ORMSearchable):
    elasticsearch.delete(index=index, id=getattr(obj, f'{index[:-1]}_id'))


event.listen(SessionLocal, 'before_commit', Searchable.before_commit)
event.listen(SessionLocal, 'after_commit', Searchable.after_commit)
