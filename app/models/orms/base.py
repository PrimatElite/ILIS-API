from datetime import datetime, timedelta
from sqlalchemy import Sequence
from sqlalchemy.ext.declarative import declarative_base
from typing import Any, Dict


DictStrAny = Dict[str, Any]


DeclarativeBase = declarative_base()


class ORMBase(DeclarativeBase):
    __abstract__ = True

    seq = Sequence('ilis_seq')

    @classmethod
    def now(cls) -> datetime:
        return datetime.utcnow() + timedelta(hours=3)

    def can_delete(self) -> bool:
        return True
