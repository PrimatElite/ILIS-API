from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class ExceptionWithMessage(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ModelNotFoundError(ExceptionWithMessage):
    pass


class ItemNotFoundError(ModelNotFoundError):
    def __init__(self, item_id: int):
        super().__init__(f'Item {item_id} not found')


class RequestNotFoundError(ModelNotFoundError):
    def __init__(self, request_id: int):
        super().__init__(f'Request {request_id} not found')


class StorageNotFoundError(ModelNotFoundError):
    def __init__(self, storage_id: int):
        super().__init__(f'Storage {storage_id} not found')


class UserNotFoundError(ModelNotFoundError):
    def __init__(self, user_id: int):
        super().__init__(f'User {user_id} not found')


class DeletionError(ExceptionWithMessage):
    pass


class RequestDurationError(ExceptionWithMessage):
    def __init__(self, duration: int, min_duration: int):
        super().__init__(f'Duration of request ({duration}s) is less than minimum duration ({min_duration}s)')


class RequestIntervalError(ExceptionWithMessage):
    def __init__(self):
        super().__init__('Current request has intersection with another request for current item')


class RequestItemError(ExceptionWithMessage):
    def __init__(self):
        super().__init__('There is no possibility for request creating on yourself item')


class UserExistingError(ExceptionWithMessage):
    def __init__(self, login_id: str, login_type: str):
        super().__init__(f'User {login_id} already registered via {login_type.lower()}')


def init_app(app: FastAPI):  # TODO make response model
    @app.exception_handler(ModelNotFoundError)
    def unicorn_exception_handler(request: Request, exc: ModelNotFoundError):
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'message': exc.message})

    @app.exception_handler(DeletionError)
    def unicorn_exception_handler(request: Request, exc: DeletionError):
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={'message': exc.message})

    @app.exception_handler(RequestDurationError)
    def unicorn_exception_handler(request: Request, exc: RequestDurationError):
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={'message': exc.message})

    @app.exception_handler(RequestIntervalError)
    def unicorn_exception_handler(request: Request, exc: RequestIntervalError):
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={'message': exc.message})

    @app.exception_handler(RequestItemError)
    def unicorn_exception_handler(request: Request, exc: RequestItemError):
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={'message': exc.message})

    @app.exception_handler(UserExistingError)
    def unicorn_exception_handler(request: Request, exc: UserExistingError):
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={'message': exc.message})
