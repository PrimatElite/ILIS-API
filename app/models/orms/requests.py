from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy import Column, DateTime, Enum, Integer
from typing import List, Optional

from .base import Base
from ..db import seq
from ..enums import EnumRequestStatus
from ...cache import cache
from ...celery import has_reserved_task
from ...redis import redis_client
from ...utils import str2datetime


STATUS_TRANSITION_RULES = {
    EnumRequestStatus.APPLIED.name: [EnumRequestStatus.BOOKED.name, EnumRequestStatus.CANCELED.name,
                                     EnumRequestStatus.DELAYED.name, EnumRequestStatus.DENIED.name],
    EnumRequestStatus.BOOKED.name: [EnumRequestStatus.CANCELED.name, EnumRequestStatus.DENIED.name,
                                    EnumRequestStatus.LENT.name],
    EnumRequestStatus.CANCELED.name: [],
    EnumRequestStatus.COMPLETED.name: [],
    EnumRequestStatus.DELAYED.name: [EnumRequestStatus.BOOKED.name, EnumRequestStatus.CANCELED.name,
                                     EnumRequestStatus.DENIED.name],
    EnumRequestStatus.DENIED.name: [],
    EnumRequestStatus.LENT.name: [EnumRequestStatus.COMPLETED.name]
}


class Requests(Base):
    __tablename__ = 'requests'

    request_id = Column(Integer, seq, primary_key=True)
    item_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    status = Column(Enum(EnumRequestStatus), default=EnumRequestStatus.APPLIED)
    count = Column(Integer, nullable=False)
    rent_starts_at = Column(DateTime, nullable=False)
    rent_ends_at = Column(DateTime, nullable=False)
    notification_sent_at = Column(DateTime)
    created_at = Column(DateTime, default=Base.now)
    updated_at = Column(DateTime, default=Base.now, onupdate=Base.now)

    serialize_properties = ['is_in_lending']

    fields_to_update = ['status', 'notification_sent_at']
    simple_fields_to_update = ['notification_sent_at']

    @property
    def is_in_lending(self) -> bool:
        return self.status in [EnumRequestStatus.BOOKED, EnumRequestStatus.LENT]

    @classmethod
    @cache.cache_list('get_requests', field='request_id')
    def get_requests(cls) -> List[dict]:
        return [cls.orm2dict(request) for request in cls.query.order_by(cls.request_id).all()]

    @classmethod
    @cache.cache_element('get_request_by_id')
    def get_request_by_id(cls, request_id: int) -> Optional[dict]:
        return cls.orm2dict(cls.query.filter_by(request_id=request_id).first())

    get_obj_by_id = get_request_by_id

    @classmethod
    @cache.cache_list('get_requests_by_item', field='request_id')
    def get_requests_by_item(cls, item_id: int) -> List[dict]:
        return [cls.orm2dict(request)
                for request in cls.query.filter_by(item_id=item_id).order_by(cls.request_id).all()]

    @classmethod
    @cache.cache_list('get_requests_by_user', field='request_id')
    def get_requests_by_user(cls, user_id: int) -> List[dict]:
        return [cls.orm2dict(request)
                for request in cls.query.filter_by(user_id=user_id).order_by(cls.request_id).all()]

    @classmethod
    @cache.cache_list('get_requests_by_item_user', field='request_id')
    def get_requests_by_item_user(cls, item_id: int, user_id: int) -> List[dict]:
        return [cls.orm2dict(request)
                for request in cls.query.filter_by(item_id=item_id, user_id=user_id).order_by(cls.request_id).all()]

    @classmethod
    def create(cls, data: dict) -> Optional[dict]:
        from .items import Items
        from .storages import Storages
        from .users import Users

        item = Items.get_item_by_id(data['item_id'])
        user = Users.get_user_by_id(data['user_id'])
        if item is None or user is None:
            return None

        storage = Storages.get_storage_by_id(item['storage_id'])
        if storage['user_id'] == user['user_id']:
            return None

        rent_start = str2datetime(data['rent_starts_at'])
        rent_end = str2datetime(data['rent_ends_at'])
        request_duration = (rent_end - rent_start).total_seconds()
        if request_duration < current_app.config['REQUEST_MIN_DURATION_SECONDS']:
            return None

        existing_requests = cls.get_requests_by_item_user(data['item_id'], data['user_id'])
        for existing_request in filter(lambda r: r['status'] in [EnumRequestStatus.BOOKED.name,
                                                                 EnumRequestStatus.DELAYED.name,
                                                                 EnumRequestStatus.LENT.name], existing_requests):
            existing_rent_start = str2datetime(existing_request['rent_starts_at'])
            existing_rent_end = str2datetime(existing_request['rent_ends_at'])
            if existing_rent_start <= rent_start < existing_rent_end or \
                    existing_rent_start <= rent_end < existing_rent_end or \
                    (rent_start < existing_rent_start and rent_end >= existing_rent_end):
                return None

        request = cls.dict2cls(data, False).add()
        request_dict = cls.orm2dict(request)
        cls.after_create(request_dict)
        return request_dict

    @classmethod
    def can_book(cls, request_dict: dict) -> bool:
        from .items import Items

        if EnumRequestStatus.BOOKED.name not in STATUS_TRANSITION_RULES[request_dict['status']]:
            return False
        return request_dict['count'] <= Items.get_remaining_count(Items.get_item_by_id(request_dict['item_id']))

    @classmethod
    def _send_notification(cls, args: List[int], rent_starts_at: datetime, rent_ends_at: datetime):
        from app.tasks import send_reminder_email

        with redis_client.lock(f'request_lock:{" ".join(map(str, args))}'):
            if has_reserved_task('app.tasks.send_reminder_email', args):
                return

            rent_duration = (rent_ends_at - rent_starts_at).total_seconds()
            eta = rent_starts_at + timedelta(seconds=int(rent_duration * current_app.config['NOTIFICATION_FACTOR']))
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

    @classmethod
    def update(cls, data: dict) -> Optional[dict]:
        request_dict = cls.get_request_by_id(data['request_id'])
        if request_dict is not None:
            if not cls._need_to_update(data):
                return request_dict
            request = cls.dict2cls(request_dict)._update_fields(data, cls.simple_fields_to_update)
            if 'status' in data:
                booked_name = EnumRequestStatus.BOOKED.name
                if data['status'] == booked_name and cls.can_book(request_dict):
                    request._update_fields(data, ['status'])
                elif data['status'] != booked_name and data['status'] in STATUS_TRANSITION_RULES[request.status.name]:
                    request._update_fields(data, ['status'])
                    if data['status'] == EnumRequestStatus.LENT.name:
                        cls.send_notification(request)
            request.add()
            request_dict = cls.orm2dict(request)
            cls.after_update(request_dict)
        return request_dict

    @classmethod
    def can_delete(cls, request_dict: dict) -> bool:
        return not request_dict['is_in_lending']

    @classmethod
    def _delete_requests(cls, requests_list: List[dict]):
        for request_dict in requests_list:
            cls._delete(request_dict)

    @classmethod
    def delete_requests_by_item(cls, item_id: int):
        cls._delete_requests(cls.get_requests_by_item(item_id))

    @classmethod
    def delete_requests_by_user(cls, user_id: int):
        cls._delete_requests(cls.get_requests_by_user(user_id))


Requests.__cached__ = [Requests.get_requests, Requests.get_requests_by_item, Requests.get_requests_by_user,
                       Requests.get_requests_by_item_user, Requests.get_request_by_id]
