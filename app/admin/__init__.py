import warnings

from flask import current_app, Flask, redirect, request, session, url_for
from flask_admin import Admin, AdminIndexView, expose, helpers
from flask_login import login_required, login_user, logout_user
from http import HTTPStatus
from urllib.parse import quote

from .login import init_app as login_init_app, is_user_authenticated, LoginForm
from .views import ItemsView, StoragesView, UsersView
from ..oauth2 import get_service
from ..models.db import db
from ..models.orms.users import Users
from ..utils.swagger_models import AuthModels


class IndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if is_user_authenticated():
            self._template_args['access_token'] = session['_token']
            return super(IndexView, self).index()
        return redirect(url_for('.login_view'))

    @expose('/login', methods=('GET', 'POST'))
    def login_view(self):
        if is_user_authenticated():
            return super(IndexView, self).index()

        data = LoginForm(request.form)
        if helpers.validate_form_on_submit(data):
            service_type = data.service.data
            service = get_service(service_type)
            redirect_uri = current_app.config['HOST'] + url_for('.login_back_view', service_type=service_type.lower())
            return redirect(service.get_code_url(redirect_uri), code=HTTPStatus.SEE_OTHER)

        return self.render('admin/login.html', form=data)

    @expose('/login/back/<service_type>')
    def login_back_view(self, service_type: str):
        service = get_service(service_type.upper())
        code = quote(request.args['code'], safe='')
        token_response, user_info = service.get_access_token(AuthModels.api, code, request.base_url)
        user_id = service.get_user_by_id(AuthModels.api, service.get_id_from_info(user_info))['user_id']
        user = Users.query.get(user_id)
        session['_token'] = token_response.access_token
        login_user(user)
        return redirect(url_for('.index'))

    @expose('/logout')
    @login_required
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))


def init_app(app: Flask):
    admin = Admin(app, 'ILIS Admin', index_view=IndexView(), base_template='master.html', template_mode='bootstrap2')
    login_init_app(app, 'admin.login_view')

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)
        admin.add_view(ItemsView(db.session))
        admin.add_view(StoragesView(db.session))
        admin.add_view(UsersView(db.session))
