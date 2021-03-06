from flask import Flask

from .db import db
from .orms import *


def init_app(app: Flask):
    db.init_app(app)
