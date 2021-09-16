from fastapi import Depends, HTTPException, Path, status
from fastapi.responses import Response
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from typing import List

from .. import schemas
from ..cruds import CRUDItems, CRUDRequests
from ..dependencies import get_admin, get_current_user, get_db
from ..models import EnumRequestStatus, ORMUsers


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
    return CRUDRequests.get_list(db)


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
    request = CRUDRequests.create(db, payload.dict())
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
    request = CRUDRequests.update(db, payload.dict())
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
def get_requests_me(user: ORMUsers = Depends(get_current_user)):
    """Get own requests"""
    requests = user.requests
    exclude = {i: {'item': {'owner': {'email', 'phone'}}}
               for i, request in enumerate(requests) if not request.in_lending}
    if len(exclude.keys()) == 0:
        return requests
    else:
        return Response(schemas.RequestMeList.from_orm(requests).json(exclude={'__root__': exclude}),
                        media_type='application/json')


@router.post(
    '/me',
    status_code=201,
    response_model=schemas.RequestMe,
    responses={
        201: {'description': 'Request created'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def create_request_me(
        payload: schemas.RequestCreateMe,
        user: ORMUsers = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Create new request"""
    data = payload.dict()
    data['user_id'] = user.user_id
    request = CRUDRequests.create(db, data)
    return Response(schemas.RequestMe.from_orm(request).json(exclude={'item': {'owner': {'email', 'phone'}}}),
                    media_type='application/json')


@router.put(
    '/me',
    response_model=schemas.RequestMe,
    responses={
        200: {'description': 'Request updated'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def update_request_me(
        payload: schemas.RequestUpdateMe,
        user: ORMUsers = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Update request"""
    request = CRUDRequests.check_existence(db, payload.request_id)
    if payload.status in [EnumRequestStatus.CANCELED]:
        if request.user_id != user.user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f'Request {payload.request_id} is not yours')
    else:
        if request.item.owner.user_id != user.user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f'Item {request.item_id} is not yours')
    request = CRUDRequests.update(db, payload.dict())
    if payload.status != request.status:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, 'Incorrect status supplied')
    if request.in_lending:
        return request
    else:
        return Response(schemas.RequestMe.from_orm(request).json(exclude={'item': {'owner': {'email', 'phone'}}}),
                        media_type='application/json')


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
        user: ORMUsers = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get requests by own item"""
    item = CRUDItems.check_existence(db, item_id)
    if item.owner.user_id != user.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f'Item {item_id} is not yours')
    requests = item.requests
    exclude = {i: {'requester': {'email', 'phone'}}
               for i, request in enumerate(requests) if not request.in_lending}
    if len(exclude.keys()) == 0:
        return requests
    else:
        return Response(schemas.RequestItemList.from_orm(requests).json(exclude={'__root__': exclude}),
                        media_type='application/json')


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
        user: ORMUsers = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get request by own item and id"""
    item = CRUDItems.check_existence(db, item_id)
    if item.owner.user_id != user.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f'Item {item_id} is not yours')
    request = CRUDRequests.check_existence(db, request_id)
    if request.item_id != item_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f'Request {request_id} is not for item {item_id}')
    if request.in_lending:
        return request
    else:
        return Response(schemas.RequestItem.from_orm(request).json(exclude={'requester': {'email', 'phone'}}),
                        media_type='application/json')


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
        user: ORMUsers = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get own request by id"""
    request = CRUDRequests.check_existence(db, request_id)
    if request.user_id != user.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f'Request {request_id} is not yours')
    if request.in_lending:
        return request
    else:
        return Response(schemas.RequestMe.from_orm(request).json(exclude={'item': {'owner': {'email', 'phone'}}}),
                        media_type='application/json')


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
    CRUDRequests.delete(db, request_id)
    return ''
