from contextlib import contextmanager
from flask_sqlalchemy import SQLAlchemy as SQLAlchemy_
from sqlalchemy import Sequence


class SQLAlchemy(SQLAlchemy_):
    @contextmanager
    def auto_commit(self, throw=True):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            if throw:
                raise e


db = SQLAlchemy()
seq = Sequence('ilis_seq')
