from flask import Flask
from flask_mail import Mail


mail = Mail()


def init_app(app: Flask):
    mail.init_app(app)
