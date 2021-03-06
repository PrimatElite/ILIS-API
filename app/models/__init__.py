from flask import Flask

from .db import db


def init_app(app: Flask):
    db.init_app(app)
