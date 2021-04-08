from flask_admin.form import rules
from flask_admin.model.base import BaseView as FlaskBaseView
from flask_sqlalchemy import BaseQuery
from jinja2.runtime import Context
from sqlalchemy.orm.scoping import scoped_session

from .base import BaseView
from ...models import Items, Storages, Users
from ...utils.swagger_models import ItemsModels
from ...utils.views import QuerySelectField


def _get_user_label(user: Users) -> str:
    label = f'{user.user_id}'
    for value in [user.name, user.surname]:
        if value is not None:
            label += f' {value}'
    return label


def _get_storages_query() -> BaseQuery:
    return Storages.query.order_by(Storages.storage_id)


def _get_storage_label(storage: Storages) -> str:
    label = f'{storage.storage_id}'
    return label


def _render_owner(view: FlaskBaseView, context: Context, model: Items, name: str) -> str:
    storage = Storages.query.filter_by(storage_id=model.storage_id).first()
    return _get_user_label(Users.query.filter_by(user_id=storage.user_id).first())


def _render_remaining_count(view: FlaskBaseView, context: Context, model: Items, name: str) -> str:
    remaining_count = model.additional_fields['remaining_count'](model.item_id)
    return f'{remaining_count}'


class ItemsView(BaseView):
    extra_columns = ['owner', 'remaining_count']

    column_default_sort = 'item_id'

    column_sortable_list = ['item_id', 'storage_id', 'name_ru', 'name_en', 'desc_ru', 'desc_en', 'count', 'created_at',
                            'updated_at']

    column_formatters = {
        'owner': _render_owner,
        'remaining_count': _render_remaining_count
    }

    column_descriptions = {field: value.description for field, value in ItemsModels.item.items()}
    column_descriptions['owner'] = 'The item owner'
    column_descriptions['remaining_count'] = 'The remaining amount of this item in storage'

    column_searchable_list = column_sortable_list

    form_create_rules = [
        rules.FieldSet(['storage_id'], 'Storage'),
        rules.FieldSet(['name_ru', 'desc_ru'], 'Name and description in Russian'),
        rules.FieldSet(['name_en', 'desc_en'], 'Name and description in English'),
        rules.FieldSet(['count'], 'Number of items')
    ]

    form_edit_rules = [
        rules.FieldSet(['name_ru', 'desc_ru'], 'Name and description in Russian'),
        rules.FieldSet(['name_en', 'desc_en'], 'Name and description in English'),
        rules.FieldSet(['count'], 'Number of items')
    ]

    form_overrides = {
        'storage_id': QuerySelectField
    }

    form_args = {
        'storage_id': {
            'query_factory': _get_storages_query,
            'get_label': _get_storage_label
        }
    }

    def __init__(self, session: scoped_session, **kwargs):
        super(ItemsView, self).__init__(Items, session, **kwargs)
