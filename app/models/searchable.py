from . import db

from ..search import elasticsearch


def query_index(index, fields, query):
    search = elasticsearch.search(index=index, doc_type=index,
                                  body={'query': {'bool': {'should': [{'wildcard': {f: f'*{query}*'}}
                                                                      for f in fields]}}})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids


def add_to_index(index, model):
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    elasticsearch.index(index=index, doc_type=index, id=getattr(model, f'{index[:-1]}_id'), body=payload)


def remove_from_index(index, model):
    elasticsearch.delete(index=index, doc_type=index, id=getattr(model, f'{index[:-1]}_id'))


class Searchable(db.Model):
    __abstract__ = True
    __searchable__ = []

    @classmethod
    def search(cls, query):
        ids = query_index(cls.__tablename__, cls.__searchable__, query)
        id_name = cls.get_id_name()
        id_column = getattr(cls, id_name)
        return [cls.orm2dict(obj) for obj in cls.query.filter(id_column.in_(ids)).order_by(id_column)]

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
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


db.event.listen(db.session, 'before_commit', Searchable.before_commit)
db.event.listen(db.session, 'after_commit', Searchable.after_commit)
