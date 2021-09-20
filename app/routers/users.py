from fastapi import Depends, Path
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session
from typing import List, Type

from .. import schemas
from ..services import Users
from ..dependencies import get_access_token, get_admin, get_current_user, get_db, get_service
from ..models import ORMUsers
from ..oauth2 import BaseOAuth2


router = APIRouter(prefix='/users', tags=['users'])


@router.get(
    '/',
    dependencies=[Depends(get_admin)],
    response_model=List[schemas.User],
    responses={
        200: {'description': 'Success'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'}
    }
)
def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    return Users.get_list(db)


@router.post(
    '/',
    dependencies=[Depends(get_admin)],
    status_code=201,
    response_model=schemas.User,
    responses={
        201: {'description': 'User created'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'}
    }
)
def create_user(
        payload: schemas.UserCreate,
        db: Session = Depends(get_db)
):
    """Create new user"""
    user = Users.create(db, payload.dict())
    return user


@router.put(
    '/',
    dependencies=[Depends(get_admin)],
    response_model=schemas.User,
    responses={
        200: {'description': 'User updated'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def update_user(
        payload: schemas.UserUpdate,
        db: Session = Depends(get_db)
):
    """Update user"""
    user = Users.update(db, payload.dict())
    return user


@router.get(
    '/me',
    response_model=schemas.User,
    responses={
        200: {'description': 'Success'},
        401: {'description': 'Unauthorized'},
        404: {'description': 'Not found'}
    }
)
def get_user_me(
        service: Type[BaseOAuth2] = Depends(get_service),
        access_token: str = Depends(get_access_token),
        db: Session = Depends(get_db)
):
    """Get user by token"""
    validation_data = service.validate_token(access_token)
    user = service.get_user_by_id(db, service.get_id_from_info(validation_data))
    data = service.transform_info(validation_data)
    data_to_update = {field: value for field, value in data.items() if getattr(user, field, '') == ''}
    if data['avatar'] != user.avatar:
        data_to_update['avatar'] = data['avatar']
    if len(data_to_update) > 0:
        data_to_update['user_id'] = user.user_id
        user = Users.update(db, data_to_update)
    return user


@router.put(
    '/me',
    response_model=schemas.User,
    responses={
        200: {'description': 'User updated'},
        401: {'description': 'Unauthorized'},
        404: {'description': 'Not found'}
    }
)
def update_user_me(
        payload: schemas.UserUpdateMe,
        user: ORMUsers = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Update user by token"""
    data = payload.dict()
    data['user_id'] = user.user_id
    user = Users.update(db, data)
    return user


@router.get(
    '/{user_id}',
    response_model=schemas.UserPublic,
    responses={
        200: {'description': 'Success'},
        404: {'description': 'Not found'}
    }
)
def get_user_by_id(
        user_id: int = Path(..., description='The identifier of the user to get'),
        db: Session = Depends(get_db)
):
    """Get user by id"""
    user = Users.check_existence(db, user_id)
    return user


@router.delete(
    '/{user_id}',
    dependencies=[Depends(get_admin)],
    status_code=204,
    responses={
        204: {'description': 'User deleted'},
        401: {'description': 'Unauthorized'},
        403: {'description': 'Forbidden operation'},
        404: {'description': 'Not found'}
    }
)
def delete_user_by_id(
        user_id: int = Path(..., description='The identifier of the user to delete'),
        db: Session = Depends(get_db)
):
    """Delete user by id"""
    Users.delete(db, user_id)
    return ''
