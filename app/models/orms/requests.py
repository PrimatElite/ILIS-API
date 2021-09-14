from datetime import datetime, timedelta
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship, Session
from typing import List, Optional

from .base import Base, DictStrAny
from .users import Users
from ..enums import EnumRequestStatus
from ...celery import has_reserved_task
from ...config import Config
from ...exceptions import ItemNotFoundError, RequestDurationError, RequestIntervalError, RequestItemError, \
    UserNotFoundError
from ...redis import redis_client
from ...utils import str2datetime


STATUS_TRANSITION_RULES = {
    EnumRequestStatus.APPLIED: [EnumRequestStatus.BOOKED, EnumRequestStatus.CANCELED, EnumRequestStatus.DELAYED,
                                EnumRequestStatus.DENIED],
    EnumRequestStatus.BOOKED: [EnumRequestStatus.CANCELED, EnumRequestStatus.DENIED, EnumRequestStatus.LENT],
    EnumRequestStatus.CANCELED: [],
    EnumRequestStatus.COMPLETED: [],
    EnumRequestStatus.DELAYED: [EnumRequestStatus.BOOKED, EnumRequestStatus.CANCELED, EnumRequestStatus.DENIED],
    EnumRequestStatus.DENIED: [],
    EnumRequestStatus.LENT: [EnumRequestStatus.COMPLETED]
}


class Requests(Base):
    __tablename__ = 'requests'

    request_id = Column(Integer, Base.seq, primary_key=True, server_default=Base.seq.next_value())
    item_id = Column(Integer, ForeignKey('items.item_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    status = Column(Enum(EnumRequestStatus), default=EnumRequestStatus.APPLIED, nullable=False)
    count = Column(Integer, nullable=False)
    rent_starts_at = Column(DateTime, nullable=False)
    rent_ends_at = Column(DateTime, nullable=False)
    notification_sent_at = Column(DateTime)
    created_at = Column(DateTime, default=Base.now, nullable=False)
    updated_at = Column(DateTime, default=Base.now, onupdate=Base.now, nullable=False)

    item = relationship('Items', back_populates='requests')
    user = relationship('Users', back_populates='requests')

    fields_to_update = [status, notification_sent_at]
    simple_fields_to_update = [notification_sent_at]

    @property
    def requester(self) -> Users:
        return self.user

    @property
    def is_in_lending(self) -> bool:
        return self.status in [EnumRequestStatus.BOOKED, EnumRequestStatus.LENT]

    @classmethod
    def get_request_by_id(cls, request_id: int, db: Session) -> Optional['Requests']:
        return db.query(cls).filter_by(request_id=request_id).first()

    get_obj_by_id = get_request_by_id

    @classmethod
    def get_requests(cls, db: Session) -> List['Requests']:
        return db.query(cls).order_by(cls.request_id).all()

    @classmethod
    def get_requests_by_item(cls, item_id: int, db: Session) -> List['Requests']:
        return db.query(cls).filter_by(item_id=item_id).order_by(cls.request_id).all()

    @classmethod
    def get_requests_by_user(cls, user_id: int, db: Session) -> List['Requests']:
        return db.query(cls).filter_by(user_id=user_id).order_by(cls.request_id).all()

    @classmethod
    def get_requests_by_item_user(cls, item_id: int, user_id: int, db: Session) -> List['Requests']:
        return db.query(cls).filter_by(item_id=item_id, user_id=user_id).order_by(cls.request_id).all()

    @classmethod
    def _check_create(cls, data: DictStrAny, db: Session):
        from .items import Items
        from .users import Users

        item = Items.get_item_by_id(data['item_id'], db)
        if item is None:
            raise ItemNotFoundError(data['item_id'])

        user = Users.get_user_by_id(data['user_id'], db)
        if user is None:
            raise UserNotFoundError(data['user_id'])

        if item.storage.user_id == user.user_id:
            raise RequestItemError()

        rent_start = data['rent_starts_at']
        rent_end = data['rent_ends_at']
        request_duration = (rent_end - rent_start).total_seconds()
        if request_duration < Config.REQUEST_MIN_DURATION_SECONDS:
            raise RequestDurationError(request_duration, Config.REQUEST_MIN_DURATION_SECONDS)

        existing_requests = cls.get_requests_by_item_user(item.item_id, user.user_id, db)
        for existing_request in filter(lambda r: r.status in [EnumRequestStatus.BOOKED.name,
                                                              EnumRequestStatus.DELAYED.name,
                                                              EnumRequestStatus.LENT.name], existing_requests):
            existing_rent_start = existing_request.rent_starts_at
            existing_rent_end = existing_request.rent_ends_at
            if existing_rent_start <= rent_start < existing_rent_end or \
                    existing_rent_start <= rent_end < existing_rent_end or \
                    (rent_start < existing_rent_start and rent_end >= existing_rent_end):
                raise RequestIntervalError()

    def can_book(self) -> bool:
        if EnumRequestStatus.BOOKED not in STATUS_TRANSITION_RULES[self.status]:
            return False
        return self.count <= self.item.remaining_count

    @classmethod
    def _send_notification(cls, args: List[int], rent_starts_at: datetime, rent_ends_at: datetime):
        from app.tasks import send_reminder_email

        with redis_client.lock(f'request_lock:{" ".join(map(str, args))}'):
            if has_reserved_task('app.tasks.send_reminder_email', args):
                return

            rent_duration = (rent_ends_at - rent_starts_at).total_seconds()
            eta = rent_starts_at + timedelta(seconds=int(rent_duration * Config.NOTIFICATION_FACTOR))
            countdown = (eta - cls.now()).total_seconds()
            send_reminder_email.apply_async(args=args, countdown=countdown)

    @classmethod
    def send_notification(cls, request: 'Requests'):
        args = [request.user_id, request.item_id, request.request_id]
        cls._send_notification(args, request.rent_starts_at, request.rent_ends_at)

    @classmethod
    def send_notification_dict(cls, request: dict):
        args = [request['user_id'], request['item_id'], request['request_id']]
        cls._send_notification(args, str2datetime(request['rent_starts_at']), str2datetime(request['rent_ends_at']))

    def _update_complicated_fields(self, data: DictStrAny, db: Session) -> 'Requests':
        if data['status'] is not None:
            if data['status'] == EnumRequestStatus.BOOKED and self.can_book():
                self.status = data['status']
            elif data['status'] != EnumRequestStatus.BOOKED and data['status'] in STATUS_TRANSITION_RULES[self.status]:
                self.status = data['status']
                if data['status'] == EnumRequestStatus.LENT:
                    self.send_notification(self)
        return self

    def can_delete(self) -> bool:
        return not self.is_in_lending
