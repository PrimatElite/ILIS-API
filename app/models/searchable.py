from flask_sqlalchemy import SignallingSession
from typing import List

from . import db
from ..search import elasticsearch


class Searchable(db.Model):
    __abstract__ = True
    __searchable__ = []

    @classmethod
    def search(cls, query: str) -> List[dict]:
        ids = query_index(cls.__tablename__, query)
        id_name = cls.get_id_name()
        id_column = getattr(cls, id_name)
        res = [cls.orm2dict(obj) for obj in cls.query.filter(id_column.in_(ids)).all()]
        return sorted(res, key=lambda obj: ids.index(obj[id_name]))

    @classmethod
    def before_commit(cls, session: SignallingSession):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session: SignallingSession):
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
    def reindex(cls):
        for obj in cls.query:
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


db.event.listen(db.session, 'before_commit', Searchable.before_commit)
db.event.listen(db.session, 'after_commit', Searchable.after_commit)
