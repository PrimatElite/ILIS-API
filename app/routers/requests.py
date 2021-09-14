from fastapi import Depends, HTTPException, Path, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from typing import List
from pydantic import parse_obj_as

from .. import schemas
from ..dependencies import get_admin, get_current_user, get_db
from ..models import EnumRequestStatus, Items, Requests, Users


router = APIRouter(prefix='/requests', tags=['requests'])


@router.get(
    '/',
    dependencies=[Depends(get_admin)],
    response_model=List[schemas.Request],
    responses={
        200: {'description': 'Success'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'}
    }
)
def get_requests(db: Session = Depends(get_db)):
    """Get all requests"""
    return Requests.get_requests(db)


@router.post(
    '/',
    dependencies=[Depends(get_admin)],
    status_code=201,
    response_model=schemas.Request,
    responses={
        201: {'description': 'Request created'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def create_request(
        payload: schemas.RequestCreate,
        db: Session = Depends(get_db)
):
    """Create new request"""
    request = Requests.create(payload.dict(), db)
    return request


@router.put(
    '/',
    dependencies=[Depends(get_admin)],
    response_model=schemas.Request,
    responses={
        200: {'description': 'Request updated'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def update_request(
        payload: schemas.RequestUpdate,
        db: Session = Depends(get_db)
):
    """Update request"""
    request = Requests.update(payload.dict(), db)
    return request


@router.get(
    '/me',
    response_model=List[schemas.RequestMe],
    responses={
        200: {'description': 'Success'},
        401: {'description': 'Unauthorized'},
        404: {'description': 'Not found'}
    }
)
def get_requests_me(user: Users = Depends(get_current_user)):
    """Get own requests"""
    requests = user.requests
    exclude = {i: {'item': {'owner': {'email', 'phone'}}}
               for i, request in enumerate(requests) if not request.is_in_lending}
    if len(exclude.keys()) == 0:
        return requests
    else:
        return JSONResponse(schemas.RequestMeList.from_orm(requests).json(exclude={'__root__': exclude}))


@router.post(
    '/me',
    status_code=201,
    response_model=schemas.Request,
    responses={
        201: {'description': 'Request created'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def create_request_me(
        payload: schemas.RequestCreate,
        user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Create new request"""
    data = payload.dict()
    data['user_id'] = user.user_id
    request = Requests.create(data, db)
    return request


@router.put(
    '/me',
    response_model=schemas.Request,
    responses={
        200: {'description': 'Request updated'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def update_request_me(
        payload: schemas.RequestUpdateMe,
        user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Update request"""
    request = Requests.check_exist(payload.request_id, db)
    if payload.status in [EnumRequestStatus.CANCELED]:
        if request.user_id != user.user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f'Request {payload.request_id} is not yours')
    else:
        if request.item.owner.user_id != user.user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f'Item {request.item_id} is not yours')
    request = Requests.update(payload.dict(), db)
    if payload.status != request.status:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, 'Incorrect status supplied')
    return request


@router.get(
    '/me/item/{item_id}',
    response_model=List[schemas.RequestItem],
    responses={
        200: {'description': 'Success'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def get_requests_me_by_item(
        item_id: int = Path(..., description='The identifier of the item to get requests'),
        user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get requests by own item"""
    item = Items.check_exist(item_id, db)
    if item.owner.user_id != user.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f'Item {item_id} is not yours')
    requests = item.requests
    exclude = {i: {'requester': {'email', 'phone'}}
               for i, request in enumerate(requests) if not request.is_in_lending}
    if len(exclude.keys()) == 0:
        return requests
    else:
        return JSONResponse(schemas.RequestItemList.from_orm(requests).json(exclude={'__root__': exclude}))


@router.get(
    '/me/item/{item_id}/request/{request_id}',
    response_model=schemas.RequestItem,
    responses={
        200: {'description': 'Success'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def get_request_me_by_item_by_id(
        item_id: int = Path(..., description='The identifier of the item to get request'),
        request_id: int = Path(..., description='The identifier of the request to get'),
        user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get request by own item and id"""
    item = Items.check_exist(item_id, db)
    if item.owner.user_id != user.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f'Item {item_id} is not yours')
    request = Requests.check_exist(request_id, db)
    if request.item_id != item_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f'Request {request_id} is not for item {item_id}')
    if request.is_in_lending:
        return request
    else:
        return JSONResponse(schemas.RequestItem.from_orm(request).json(exclude={'requester': {'email', 'phone'}}))


@router.get(
    '/me/{request_id}',
    response_model=schemas.RequestMe,
    responses={
        200: {'description': 'Success'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def get_request_me_by_id(
        request_id: int = Path(..., description='The identifier of the request to get'),
        user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get own request by id"""
    request = Requests.check_exist(request_id, db)
    if request.user_id != user.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f'Request {request_id} is not yours')
    if request.is_in_lending:
        return request
    else:
        return JSONResponse(schemas.RequestMe.from_orm(request).json(exclude={'item': {'owner': {'email', 'phone'}}}))


@router.delete(
    '/{request_id}',
    dependencies=[Depends(get_admin)],
    status_code=204,
    responses={
        204: {'description': 'Request deleted'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def delete_request_by_id(
        request_id: int = Path(..., description='The identifier of the request to delete'),
        db: Session = Depends(get_db)
):
    """Delete request by id"""
    Requests.delete(request_id, db)
    return ''
