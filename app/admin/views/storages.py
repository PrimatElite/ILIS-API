from flask_admin.form import rules
from flask_admin.model.base import BaseView as FlaskBaseView
from flask_sqlalchemy import BaseQuery
from jinja2.runtime import Context
from sqlalchemy.orm.scoping import scoped_session

from .base import BaseView
from ...models import Storages, Users
from ...utils.swagger_models import StoragesModels
from ...utils.views import get_user_label as _get_user_label, QuerySelectField


def _get_users_query() -> BaseQuery:
    return Users.query.order_by(Users.user_id)


def _render_owner(view: FlaskBaseView, context: Context, model: Storages, name: str) -> str:
    return _get_user_label(Users.query.filter_by(user_id=model.user_id).first())


class StoragesView(BaseView):
    extra_columns = ['owner']

    column_default_sort = 'storage_id'

    column_sortable_list = ['user_id', 'storage_id', 'name', 'latitude', 'longitude', 'address']

    column_formatters = {
        'owner': _render_owner
    }

    column_descriptions = {field: value.description for field, value in StoragesModels.storage.items()}
    column_descriptions['owner'] = 'The storage owner'

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
        }
    }

    def __init__(self, session: scoped_session, **kwargs):
        super(StoragesView, self).__init__(Storages, session, **kwargs)
