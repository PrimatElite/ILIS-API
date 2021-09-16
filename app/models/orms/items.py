from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .searchable import ORMSearchable
from .users import ORMUsers


class ORMItems(ORMSearchable):
    __tablename__ = 'items'

    item_id = Column(Integer, ORMSearchable.seq, primary_key=True, server_default=ORMSearchable.seq.next_value())
    storage_id = Column(Integer, ForeignKey('storages.storage_id'), nullable=False)
    name_ru = Column(String(length=127), nullable=False)
    name_en = Column(String(length=127), nullable=False)
    desc_ru = Column(String(length=511), nullable=False)
    desc_en = Column(String(length=511), nullable=False)
    count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=ORMSearchable.now, nullable=False)
    updated_at = Column(DateTime, default=ORMSearchable.now, onupdate=ORMSearchable.now, nullable=False)

    storage = relationship('ORMStorages', back_populates='items')
    requests = relationship('ORMRequests', back_populates='item', cascade='all, delete')

    __searchable__ = [name_ru, name_en, desc_ru, desc_en]

    @property
    def owner(self) -> ORMUsers:
        return self.storage.owner

    @property
    def remaining_count(self) -> int:
        requests_filter = filter(lambda request: request.in_lending, self.requests)
        lending_count = sum(map(lambda request: request.count, requests_filter))
        return self.count - lending_count

    def can_delete(self) -> bool:
        return all(request.can_delete() for request in self.requests)
