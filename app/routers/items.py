from fastapi import Depends, HTTPException, Path, Query, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from typing import List

from .. import schemas
from ..dependencies import get_admin, get_current_user, get_db, get_trimmed_query
from ..models import Items, Storages, Users


router = APIRouter(prefix='/items', tags=['items'])


@router.get(
    '/',
    dependencies=[Depends(get_admin)],
    response_model=List[schemas.Item],
    responses={
        200: {'description': 'Success'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'}
    }
)
def get_items(db: Session = Depends(get_db)):
    """Get all items"""
    return Items.get_items(db)


@router.post(
    '/',
    dependencies=[Depends(get_admin)],
    status_code=201,
    response_model=schemas.Item,
    responses={
        201: {'description': 'Item created'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def create_item(
        payload: schemas.ItemCreate,
        db: Session = Depends(get_db)
):
    """Create new item"""
    item = Items.create(payload.dict(), db)
    return item


@router.put(
    '/',
    dependencies=[Depends(get_admin)],
    response_model=schemas.Item,
    responses={
        200: {'description': 'Item updated'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def update_item(
        payload: schemas.ItemUpdate,
        db: Session = Depends(get_db)
):
    """Update item"""
    item = Items.update(payload.dict(), db)
    return item


@router.post(
    '/me',
    status_code=201,
    response_model=schemas.Item,
    responses={
        201: {'description': 'Item created'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def create_item_me(
        payload: schemas.ItemCreate,
        user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Create new item in own storage"""
    storage = Storages.check_exist(payload.storage_id, db)
    if storage.user_id != user.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f'Storage {payload.storage_id} is not yours')
    item = Items.create(payload.dict(), db)
    return item


@router.put(
    '/me',
    response_model=schemas.Item,
    responses={
        200: {'description': 'Item updated'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def update_item_me(
        payload: schemas.ItemUpdate,
        user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Update item in own storage"""
    item = Items.check_exist(payload.item_id, db)
    if item.owner.user_id != user.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f'Item {payload.item_id} is not yours')
    item = Items.update(payload.dict(), db)
    return item


@router.get(
    '/me/storage/{storage_id}',
    response_model=List[schemas.Item],
    responses={
        200: {'description': 'Success'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def get_items_me_by_storage(
        storage_id: int = Path(..., description='The identifier of the storage to get items'),
        user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get items from own storage"""
    storage = Storages.check_exist(storage_id, db)
    if storage.user_id != user.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f'Storage {storage_id} is not yours')
    items = storage.items
    return items


@router.delete(
    '/me/{item_id}',
    status_code=204,
    responses={
        204: {'description': 'Item deleted'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def delete_item_me_by_id(
        item_id: int = Path(..., description='The identifier of the item to delete'),
        user: Users = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Delete item in own storage by id"""
    item = Items.check_exist(item_id, db)
    if item.owner.user_id != user.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f'Item {item_id} is not yours')
    Items.delete(item_id, db)
    return ''


@router.get(
    '/storage/{storage_id}',
    dependencies=[Depends(get_admin)],
    response_model=List[schemas.Item],
    responses={
        200: {'description': 'Success'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def get_items_by_storage(
        storage_id: int = Path(..., description='The identifier of the storage to get items'),
        db: Session = Depends(get_db)
):
    """Get items by storage"""
    storage = Storages.check_exist(storage_id, db)
    items = storage.items
    return items


@router.get(
    '/search',
    response_model=List[schemas.ItemPublic],
    responses={200: {'description': 'Success'}}
)
def search_items(
        query: str = Depends(get_trimmed_query('query', ..., description='The required items search query')),
        db: Session = Depends(get_db)
):
    """Search items by name and description"""
    items = Items.search(query, db)
    return items


@router.get(
    '/{item_id}',
    response_model=schemas.ItemPublic,
    responses={
        200: {'description': 'Success'},
        404: {'description': 'Not found'}
    }
)
def get_item_by_id(
        item_id: int = Path(..., description='The identifier of the item to get'),
        db: Session = Depends(get_db)
):
    """Get item by id"""
    item = Items.check_exist(item_id, db)
    return item


@router.delete(
    '/{item_id}',
    dependencies=[Depends(get_admin)],
    status_code=204,
    responses={
        204: {'description': 'Item deleted'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def delete_item_by_id(
        item_id: int = Path(..., description='The identifier of the item to delete'),
        db: Session = Depends(get_db)
):
    """Delete item by id"""
    Items.delete(item_id, db)
    return ''
