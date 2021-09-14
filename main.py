import uvicorn

from os import environ

from app import init_app


app = init_app()


if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=int(environ['PORT']), reload=True)
