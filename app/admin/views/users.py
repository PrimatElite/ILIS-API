from flask_admin.form import rules
from flask_admin.model.base import BaseView as FlaskBaseView
from jinja2 import Markup
from jinja2.runtime import Context
from sqlalchemy.orm.scoping import scoped_session

from .base import BaseView
from ...models.orms.users import Users
from ...utils.swagger_models import UsersModels


def _render_avatar(view: FlaskBaseView, context: Context, model: Users, name: str):
    if model.avatar is None:
        return ''
    return Markup(f'<img src="{model.avatar}">')


class UsersView(BaseView):
    column_default_sort = 'user_id'

    column_sortable_list = ['user_id', 'login_type', 'name', 'surname', 'email', 'phone', 'role', 'created_at',
                            'updated_at']

    column_exclude_list = ['login_id']

    column_formatters = {
        'avatar': _render_avatar
    }

    column_descriptions = {field: value.description for field, value in UsersModels.user.items()}

    column_searchable_list = column_sortable_list

    form_create_rules = [
        rules.FieldSet(['login_id', 'login_type'], 'Authorization service'),
        rules.FieldSet(['name', 'surname', 'email', 'phone', 'avatar'], 'Personal'),
        rules.FieldSet(['role'], 'Access')
    ]

    form_edit_rules = [
        rules.FieldSet(['name', 'surname', 'email', 'phone'], 'Personal'),
        rules.FieldSet(['role'], 'Access')
    ]

    def __init__(self, session: scoped_session, **kwargs):
        super(UsersView, self).__init__(Users, session, **kwargs)

    def on_model_delete(self, model: Users):
        # TODO add check for deleting
        pass
