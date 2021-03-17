from flask_admin.form import rules
from sqlalchemy.orm.scoping import scoped_session

from .base import BaseView
from ...models.orms.users import Storages
from ...utils.swagger_models import StoragesModels


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

    def __init__(self, session: scoped_session, **kwargs):
        super(StoragesView, self).__init__(Storages, session, **kwargs)
