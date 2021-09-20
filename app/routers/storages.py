from fastapi import Depends, HTTPException, Path, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from typing import List

from .. import schemas
from ..services import Storages, Users
from ..dependencies import get_admin, get_current_user, get_db
from ..models import ORMUsers


router = APIRouter(prefix='/storages', tags=['storages'])


@router.get(
    '/',
    dependencies=[Depends(get_admin)],
    response_model=List[schemas.Storage],
    responses={
        200: {'description': 'Success'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'}
    }
)
def get_storages(db: Session = Depends(get_db)):
    """Get all storages"""
    return Storages.get_list(db)


@router.post(
    '/',
    dependencies=[Depends(get_admin)],
    status_code=201,
    response_model=schemas.Storage,
    responses={
        201: {'description': 'Storage created'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def create_storage(
        payload: schemas.StorageCreate,
        db: Session = Depends(get_db)
):
    """Create new storage"""
    storage = Storages.create(db, payload.dict())
    return storage


@router.put(
    '/',
    dependencies=[Depends(get_admin)],
    response_model=schemas.Storage,
    responses={
        200: {'description': 'Storage updated'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def update_storage(
        payload: schemas.StorageUpdate,
        db: Session = Depends(get_db)
):
    """Update storage"""
    storage = Storages.update(db, payload.dict())
    return storage


@router.get(
    '/me',
    response_model=List[schemas.Storage],
    responses={
        200: {'description': 'Success'},
        401: {'description': 'Unauthorized'},
        404: {'description': 'Not found'}
    }
)
def get_storages_me(user: ORMUsers = Depends(get_current_user)):
    """Get own storages"""
    storages = user.storages
    return storages


@router.post(
    '/me',
    status_code=201,
    response_model=schemas.Storage,
    responses={
        201: {'description': 'Storage created'},
        401: {'description': 'Unauthorized'},
        404: {'description': 'Not found'}
    }
)
def create_storage_me(
        payload: schemas.StorageCreateMe,
        user: ORMUsers = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Create new own storage"""
    data = payload.dict()
    data['user_id'] = user.user_id
    storage = Storages.create(db, data)
    return storage


@router.put(
    '/me',
    response_model=schemas.Storage,
    responses={
        200: {'description': 'Storage updated'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def update_storage_me(
        payload: schemas.StorageUpdateMe,
        user: ORMUsers = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Update own storage"""
    storage = Storages.check_existence(db, payload.storage_id)
    if storage.user_id != user.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f'Storage {payload.storage_id} is not yours')
    storage = Storages.update(db, payload.dict())
    return storage


@router.delete(
    '/me/{storage_id}',
    status_code=204,
    responses={
        204: {'description': 'Storage deleted'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def delete_storage_me_by_id(
        storage_id: int = Path(..., description='The identifier of the storage to delete'),
        user: ORMUsers = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Delete own storage by id"""
    storage = Storages.check_existence(db, storage_id)
    if storage.user_id != user.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f'Storage {storage_id} is not yours')
    Storages.delete(db, storage_id)
    return ''


@router.get(
    '/user/{user_id}',
    dependencies=[Depends(get_admin)],
    response_model=List[schemas.Storage],
    responses={
        200: {'description': 'Success'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def get_storages_by_user(
        user_id: int = Path(..., description='The identifier of the user to get storages'),
        db: Session = Depends(get_db)
):
    """Get storages by user"""
    user = Users.check_existence(db, user_id)
    storages = user.storages
    return storages


@router.delete(
    '/{storage_id}',
    dependencies=[Depends(get_admin)],
    status_code=204,
    responses={
        204: {'description': 'Storage deleted'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def delete_storage_by_id(
        storage_id: int = Path(..., description='The identifier of the storage to delete'),
        db: Session = Depends(get_db)
):
    """Delete storage by id"""
    Storages.delete(db, storage_id)
    return ''
