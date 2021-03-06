from flask.wrappers import Response

from app import create_app
from app.models import db


app = create_app()


@app.after_request
def after_request(response: Response) -> Response:
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Access-Control-Allow-Headers, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.cli.command()
def resetdb():
    db.drop_all()
    db.create_all()


@app.cli.command()
def createdb():
    db.create_all()
