from flask_admin.form import rules
from flask_sqlalchemy import BaseQuery
from sqlalchemy.orm.scoping import scoped_session

from .base import BaseView
from ...models import Storages, Users
from ...utils.swagger_models import StoragesModels
from ...utils.views import QuerySelectField


def _get_users_query() -> BaseQuery:
    return Users.query.order_by(Users.user_id)


def _get_user_label(user: Users) -> str:
    label = f'{user.user_id}'
    for value in [user.name, user.surname]:
        if value is not None:
            label += f' {value}'
    return label


class StoragesView(BaseView):
    column_default_sort = 'storage_id'

    column_sortable_list = ['user_id', 'storage_id', 'name', 'latitude', 'longitude', 'address']

    column_descriptions = {field: value.description for field, value in StoragesModels.storage.items()}

    column_searchable_list = column_sortable_list

    form_create_rules = [
        rules.FieldSet(['user_id'], 'Owner'),
        rules.FieldSet(['name', 'latitude', 'longitude', 'address'], 'Information')
    ]

    form_edit_rules = [
        rules.FieldSet(['name', 'latitude', 'longitude', 'address'], 'Information'),
    ]

    form_overrides = {
        'user_id': QuerySelectField
    }

    form_args = {
        'user_id': {
            'query_factory': _get_users_query,
            'get_label': _get_user_label
        },
    }

    def __init__(self, session: scoped_session, **kwargs):
        super(StoragesView, self).__init__(Storages, session, **kwargs)
