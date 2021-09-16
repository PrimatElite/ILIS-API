from datetime import datetime, timedelta
from typing import List

from .base import CRUDBase, DictStrAny, Session
from .items import CRUDItems
from .users import CRUDUsers
from ..celery import has_reserved_task
from ..config import Config
from ..exceptions import ItemNotFoundError, RequestDurationError, RequestIntervalError, RequestItemError, \
    UserNotFoundError
from ..models import EnumRequestStatus, ORMRequests, REQUEST_STATUS_TRANSITION_RULES
from ..redis import redis_client


class CRUDRequests(CRUDBase):
    model = ORMRequests

    fields_to_update = [ORMRequests.status, ORMRequests.notification_sent_at]
    simple_fields_to_update = [ORMRequests.notification_sent_at]

    @classmethod
    def get_requests_by_item_user(cls, db: Session, item_id: int, user_id: int) -> List[ORMRequests]:
        return db.query(cls.model).filter_by(item_id=item_id, user_id=user_id).order_by(cls.model.request_id).all()

    @classmethod
    def _check_creation(cls, db: Session, data: DictStrAny):
        item = CRUDItems.get_by_id(db, data['item_id'])
        if item is None:
            raise ItemNotFoundError(data['item_id'])

        user = CRUDUsers.get_by_id(db, data['user_id'])
        if user is None:
            raise UserNotFoundError(data['user_id'])

        if item.storage.user_id == user.user_id:
            raise RequestItemError()

        rent_start = data['rent_starts_at']
        rent_end = data['rent_ends_at']
        request_duration = (rent_end - rent_start).total_seconds()
        if request_duration < Config.REQUEST_MIN_DURATION_SECONDS:
            raise RequestDurationError(request_duration, Config.REQUEST_MIN_DURATION_SECONDS)

        existing_requests = cls.get_requests_by_item_user(db, item.item_id, user.user_id)
        for existing_request in filter(lambda r: r.status in [EnumRequestStatus.BOOKED, EnumRequestStatus.DELAYED,
                                                              EnumRequestStatus.LENT], existing_requests):
            existing_rent_start = existing_request.rent_starts_at
            existing_rent_end = existing_request.rent_ends_at
            if existing_rent_start <= rent_start < existing_rent_end or \
                    existing_rent_start <= rent_end < existing_rent_end or \
                    (rent_start < existing_rent_start and rent_end >= existing_rent_end):
                raise RequestIntervalError()

    @classmethod
    def _send_notification(cls, args: List[int], rent_starts_at: datetime, rent_ends_at: datetime):
        from app.tasks import send_reminder_email

        with redis_client.lock(f'request_lock:{" ".join(map(str, args))}'):
            if has_reserved_task('app.tasks.send_reminder_email', args):
                return

            rent_duration = (rent_ends_at - rent_starts_at).total_seconds()
            eta = rent_starts_at + timedelta(seconds=int(rent_duration * Config.NOTIFICATION_FACTOR))
            countdown = (eta - cls.model.now()).total_seconds()
            send_reminder_email.apply_async(args=args, countdown=countdown)

    @classmethod
    def send_notification(cls, request: ORMRequests):
        args = [request.user_id, request.item_id, request.request_id]
        cls._send_notification(args, request.rent_starts_at, request.rent_ends_at)

    @classmethod
    def _update_complicated_fields(cls, db: Session, obj: ORMRequests, data: DictStrAny) -> ORMRequests:
        if data.get('status') is not None:
            if data['status'] == EnumRequestStatus.BOOKED and obj.can_book():
                obj.status = data['status']
            elif data['status'] != EnumRequestStatus.BOOKED and \
                    data['status'] in REQUEST_STATUS_TRANSITION_RULES[obj.status]:
                obj.status = data['status']
                if data['status'] == EnumRequestStatus.LENT:
                    cls.send_notification(obj)
        return obj
