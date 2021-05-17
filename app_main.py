from flask import request
from flask.wrappers import Response
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import init_app
from app.models import db


app = init_app()
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@app.after_request
def after_request(response: Response) -> Response:
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Access-Control-Allow-Headers, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    if app.config['LOG_ERRORS'] and response.status_code >= 400:
        app.logger.error(f'Request url: {request.url}\n'
                         f'Request headers: {request.headers}\n'
                         f'Request data: {request.get_data()}\n'
                         f'Response status: {response.status}\n'
                         f'Response data: {response.get_data()}')
    return response


@app.cli.command()
def resetdb():
    db.drop_all()
    db.create_all()


@app.cli.command()
def createdb():
    db.create_all()


if __name__ == '__main__':
    manager.run()
