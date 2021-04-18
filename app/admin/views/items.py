import logging

from flask import flash
from flask_admin.babel import gettext
from flask_admin.form import BaseForm, rules
from flask_admin.model.base import BaseView as FlaskBaseView
from flask_sqlalchemy import BaseQuery
from jinja2.runtime import Context
from sqlalchemy.orm.scoping import scoped_session
from typing import Type

from .base import BaseView
from ...models import Items, Storages, Users
from ...utils.swagger_models import ItemsModels
from ...utils.views import get_user_label, QuerySelectField

# Set up logger
log = logging.getLogger("flask-admin.sqla")


def _get_storages_query() -> BaseQuery:
    return Storages.query.order_by(Storages.storage_id)


def _get_storage_label(storage: Storages) -> str:
    return f'{storage.storage_id} {storage.name}'


def _render_owner(view: FlaskBaseView, context: Context, model: Items, name: str) -> str:
    storage = Storages.query.filter_by(storage_id=model.storage_id).subquery()
    return get_user_label(Users.query.filter_by(user_id=storage.c.user_id).first())


def _render_remaining_count(view: FlaskBaseView, context: Context, model: Items, name: str) -> str:
    remaining_count = Items.additional_fields['remaining_count'](model.item_id)
    return f'{remaining_count}'


def _render_storage(view: FlaskBaseView, context: Context, model: Items, name: str) -> str:
    return _get_storage_label(Storages.query.filter_by(storage_id=model.storage_id).first())


class ItemsView(BaseView):
    extra_columns = ['owner', 'remaining_count', 'storage']

    column_default_sort = 'item_id'

    column_sortable_list = ['item_id', 'storage_id', 'name_ru', 'name_en', 'desc_ru', 'desc_en', 'count', 'created_at',
                            'updated_at']

    column_formatters = {
        'owner': _render_owner,
        'remaining_count': _render_remaining_count,
        'storage': _render_storage
    }

    column_descriptions = {field: value.description for field, value in ItemsModels.item.items()}
    column_descriptions['owner'] = 'The item owner'
    column_descriptions['remaining_count'] = 'The remaining amount of this item in storage'
    column_descriptions['storage'] = 'The item storage'

    column_searchable_list = column_sortable_list

    form_create_rules = [
        rules.FieldSet(['storage_id'], 'Storage'),
        rules.FieldSet(['name_ru', 'desc_ru'], 'Name and description in Russian'),
        rules.FieldSet(['name_en', 'desc_en'], 'Name and description in English'),
        rules.FieldSet(['count'], 'Number of items')
    ]

    form_edit_rules = [
        rules.FieldSet(['storage_id'], 'Storage'),
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

    def update_model(self, form, model):
        """
            Update model from form.

            :param form:
                Form instance
            :param model:
                Model instance
        """
        try:
            self._on_model_change(form, model, False)
            form.populate_obj(model)
            self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to update record. %(error)s', error=str(ex)), 'error')
                log.exception('Failed to update record.')

            self.session.rollback()

            return False
        else:
            self.after_model_change(form, model, False)

        return True

    def on_model_change(self, form: Type[BaseForm], model: Items, is_created: bool):
        if not is_created:
            if form.data['count'] < model.count - Items.additional_fields['remaining_count'](model.item_id)\
                    or form.data['count'] < 1:
                raise Exception(f'Item {model.item_id} count can\'t be changed')
            old_storage = Storages.query.filter_by(storage_id=model.storage_id).first()
            if form.data['storage_id'].user_id != old_storage.user_id:
                raise Exception(f'Item {model.item_id} storage can\'t be changed to another user')
