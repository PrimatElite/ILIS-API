from flask import current_app
from flask_admin.form import BaseForm, rules
from flask_admin.model.base import BaseView as FlaskBaseView
from flask_sqlalchemy import BaseQuery
from jinja2.runtime import Context
from sqlalchemy.orm.scoping import scoped_session
from typing import Type

from .base import BaseView
from ...models import Items, Requests, Storages, Users
from ...models.enums import EnumRequestStatus
from ...models.orms.requests import STATUS_TRANSITION_RULES
from ...utils import str2datetime
from ...utils.swagger_models import RequestsModels
from ...utils.views import get_user_label, QuerySelectField


def _get_users_query() -> BaseQuery:
    return Users.query.order_by(Users.user_id)


def _get_items_query() -> BaseQuery:
    return Items.query.order_by(Items.item_id)


def _get_item_label(item: Items) -> str:
    return f'{item.item_id} {item.name_en}'


def _render_requester(view: FlaskBaseView, context: Context, model: Requests, name: str) -> str:
    return get_user_label(Users.query.filter_by(user_id=model.user_id).first())


def _render_item(view: FlaskBaseView, context: Context, model: Requests, name: str) -> str:
    return _get_item_label(Items.query.filter_by(item_id=model.item_id).first())


class RequestsView(BaseView):
    extra_columns = ['requester', 'item']

    column_default_sort = 'request_id'

    column_sortable_list = ['request_id', 'item_id', 'user_id', 'status', 'count', 'rent_starts_at', 'rent_ends_at',
                            'notification_sent_at', 'created_at', 'updated_at']

    column_formatters = {
        'requester': _render_requester,
        'item': _render_item
    }

    column_descriptions = {field: value.description for field, value in RequestsModels.request.items()}
    column_descriptions['requester'] = 'The item requester'
    column_descriptions['item'] = 'The requested item'

    column_searchable_list = column_sortable_list

    form_create_rules = [
        rules.FieldSet(['user_id'], 'Requester'),
        rules.FieldSet(['item_id'], 'Item'),
        rules.FieldSet(['count', 'rent_starts_at', 'rent_ends_at'], 'Rent data')
    ]

    form_edit_rules = [
        rules.FieldSet(['status'], 'Request status')
    ]

    form_overrides = {
        'user_id': QuerySelectField,
        'item_id': QuerySelectField
    }

    form_args = {
        'user_id': {
            'query_factory': _get_users_query,
            'get_label': get_user_label
        },
        'item_id': {
            'query_factory': _get_items_query,
            'get_label': _get_item_label
        }
    }

    def __init__(self, session: scoped_session, **kwargs):
        super(RequestsView, self).__init__(Requests, session, **kwargs)

    def on_model_change(self, form: Type[BaseForm], model: Requests, is_created: bool):
        if is_created:
            storage = Storages.get_storage_by_id(form.data['item_id'].storage_id)
            if storage['user_id'] == form.data['user_id'].user_id:
                raise Exception(f'Request can\'t be created. Invalid requested item')

            request_duration = (form.data['rent_ends_at'] - form.data['rent_starts_at']).total_seconds()
            if request_duration < current_app.config['REQUEST_MIN_DURATION_SECONDS']:
                raise Exception(f'Request can\'t be created. Invalid rent duration')

            requests = Requests.get_requests_by_item_user(form.data['item_id'].item_id, form.data['user_id'].user_id)
            for request in filter(lambda r: r['status'] in [EnumRequestStatus.BOOKED.name,
                                                            EnumRequestStatus.DELAYED.name,
                                                            EnumRequestStatus.LENT.name], requests):
                rent_start = str2datetime(request['rent_starts_at'])
                rent_end = str2datetime(request['rent_ends_at'])
                if rent_start <= form.data['rent_starts_at'] < rent_end or \
                        rent_start <= form.data['rent_ends_at'] < rent_end or \
                        (form.data['rent_starts_at'] < rent_start and form.data['rent_ends_at'] >= rent_end):
                    raise Exception(f'Request can\'t be created. Invalid rent date interval')
        else:
            booked_name = EnumRequestStatus.BOOKED.name
            if (form.data['status'] == booked_name and not Requests.can_book(Requests.orm2dict(model))) or \
                    (form.data['status'] != booked_name and
                     form.data['status'] not in STATUS_TRANSITION_RULES[model.status.name]):
                raise Exception(f'Request {model.request_id} status can\'t be changed')
