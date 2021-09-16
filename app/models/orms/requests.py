from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import ORMBase
from .users import ORMUsers
from ..enums import EnumRequestStatus


REQUEST_STATUS_TRANSITION_RULES = {
    EnumRequestStatus.APPLIED: [EnumRequestStatus.BOOKED, EnumRequestStatus.CANCELED, EnumRequestStatus.DELAYED,
                                EnumRequestStatus.DENIED],
    EnumRequestStatus.BOOKED: [EnumRequestStatus.CANCELED, EnumRequestStatus.DENIED, EnumRequestStatus.LENT],
    EnumRequestStatus.CANCELED: [],
    EnumRequestStatus.COMPLETED: [],
    EnumRequestStatus.DELAYED: [EnumRequestStatus.BOOKED, EnumRequestStatus.CANCELED, EnumRequestStatus.DENIED],
    EnumRequestStatus.DENIED: [],
    EnumRequestStatus.LENT: [EnumRequestStatus.COMPLETED]
}


class ORMRequests(ORMBase):
    __tablename__ = 'requests'

    request_id = Column(Integer, ORMBase.seq, primary_key=True, server_default=ORMBase.seq.next_value())
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    status = Column(Enum(EnumRequestStatus), default=EnumRequestStatus.APPLIED, nullable=False)
    count = Column(Integer, nullable=False)
    rent_starts_at = Column(DateTime, nullable=False)
    rent_ends_at = Column(DateTime, nullable=False)
    notification_sent_at = Column(DateTime)
    created_at = Column(DateTime, default=ORMBase.now, nullable=False)
    updated_at = Column(DateTime, default=ORMBase.now, onupdate=ORMBase.now, nullable=False)

    item = relationship('ORMItems', back_populates='requests')
    requester = relationship('ORMUsers', back_populates='requests')

    @property
    def in_lending(self) -> bool:
        return self.status in [EnumRequestStatus.BOOKED, EnumRequestStatus.LENT]

    def can_book(self) -> bool:
        if EnumRequestStatus.BOOKED not in REQUEST_STATUS_TRANSITION_RULES[self.status]:
            return False
        return self.count <= self.item.remaining_count

    def can_delete(self) -> bool:
        return not self.in_lending
