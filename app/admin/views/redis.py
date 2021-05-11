from flask import current_app, flash, redirect, Response
from flask_admin.contrib import rediscli
from flask_login import login_url
from redis import StrictRedis

from ..login import is_user_authenticated


class RedisView(rediscli.RedisCli):
    def __init__(self, client: StrictRedis, **kwargs):
        super(RedisView, self).__init__(client, **kwargs)

    def is_accessible(self) -> bool:
        return is_user_authenticated()

    def inaccessible_callback(self, name: str, **kwargs) -> Response:
        flash('Please, log in', 'error')
        return redirect(login_url(current_app.login_manager.login_view))
