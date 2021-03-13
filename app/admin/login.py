from flask import flash, Flask, session
from flask_login import current_user, LoginManager, logout_user
from wtforms import form, fields, validators

from ..models.enums import EnumLoginService, EnumUserRole
from ..models.orms.users import Users
from ..oauth2 import get_service
from ..utils.swagger_models import AuthModels


def init_app(app: Flask, login_view: str):
    login_manager = LoginManager()
    login_manager.login_view = login_view
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(user_id)


def is_user_authenticated():
    if not current_user.is_authenticated or current_user.role != EnumUserRole.ADMIN:
        return False

    service = get_service(current_user.login_type.name)
    try:
        validation_data = service.validate_token(AuthModels.api, session['_token'])
    except:
        flash('Session expired', 'error')
        logout_user()
        return False
    data = service.transform_info(validation_data)
    user = Users.orm2dict(current_user)

    data_to_update = {field: value for field, value in data.items() if user[field] is None}
    if data['avatar'] != user['avatar']:
        data_to_update['avatar'] = data['avatar']
    if len(data_to_update) > 0:
        data_to_update['user_id'] = user['user_id']
        Users.update(data_to_update)

    return True


class LoginForm(form.Form):
    service = fields.SelectField(validators=[validators.required()], choices=list(EnumLoginService.__members__),
                                 label='Select the service for login')
