from flask import render_template
from flask_mail import Message
from typing import List

from . import app
from .celery import celery
from .mail import mail
from .utils import datetime2str, str2datetime


def send_email(subject: str, recipients: List[str], text_body: str, html_body: str):
    msg = Message(subject, recipients, text_body, html_body)
    mail.send(msg)


@celery.task
def send_reminder_email(user_id: int, item_id: int, request_id: int):
    with app.app_context():
        from .models import Items, Users, Requests

        user = Users.get_user_by_id(user_id)
        item = Items.get_item_by_id(item_id)
        request = Requests.get_request_by_id(request_id)

        rent_end = str2datetime(request['rent_ends_at'])
        rent_ends_on = rent_end.date().isoformat().replace('-', '.')
        rent_ends_at = rent_end.time().isoformat()[:5]

        text_body = render_template('reminder_email.txt', username=user['name'], usersurname=user['surname'],
                                    itemname=item['name_en'], rent_ends_on=rent_ends_on, rent_ends_at=rent_ends_at)
        html_body = render_template('reminder_email.html', username=user['name'], usersurname=user['surname'],
                                    itemname=item['name_en'], rent_ends_on=rent_ends_on, rent_ends_at=rent_ends_at)

        send_email('[ILIS] item return reminder', [user['email']], text_body, html_body)
        data = {'request_id': request_id, 'notification_sent_at': datetime2str(Requests.now())}
        Requests.update(data)


@celery.task
def set_tasks():
    with app.app_context():
        from .models import Requests
        from .models.orms.requests import EnumRequestStatus

        for request in Requests.get_requests():
            if request['status'] == EnumRequestStatus.LENT.name and request['notification_sent_at'] is None:
                Requests.send_notification_dict(request)
