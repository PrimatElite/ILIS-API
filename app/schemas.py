from datetime import datetime
from typing import Any, Dict, List, Union
from pydantic import BaseModel as BaseModel_, Field

from .models.enums import *


class BaseModel(BaseModel_):
    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        if 'exclude_unset' not in kwargs:
            kwargs['exclude_unset'] = True
        return super().dict(*args, **kwargs)


class TrimModel(BaseModel):
    class Config:
        anystr_strip_whitespace = True


class Version(BaseModel):
    version: str = Field(..., description='The number of version')


class UserCreate(TrimModel):
    login_id: str = Field(..., description='The user login identifier')
    login_type: EnumLoginService = Field(..., description='The user login service type')
    name: str = Field(None, description='The user name')
    surname: str = Field(None, description='The user surname')
    role: EnumUserRole = Field(..., description='The user role')
    email: str = Field(None, description='The user email')
    phone: str = Field(None, description='The user phone')
    avatar: str = Field(None, description='The user avatar')


class UserUpdateMe(TrimModel):
    name: str = Field(None, description='The user name')
    surname: str = Field(None, description='The user surname')
    email: str = Field(None, description='The user email')
    phone: str = Field(None, description='The user avatar')


class UserUpdate(UserUpdateMe):
    user_id: int = Field(..., description='The user unique identifier', gt=0)
    role: EnumUserRole = Field(None, description='The user role')


class UserPublic(TrimModel):
    user_id: int = Field(..., description='The user unique identifier', gt=0)
    name: str = Field(..., description='The user name')
    surname: str = Field(..., description='The user surname')
    role: EnumUserRole = Field(..., description='The user role')
    avatar: str = Field(..., description='The user avatar')

    class Config(TrimModel.Config):
        orm_mode = True


class UserWithContacts(UserPublic):
    email: str = Field(..., description='The user email')
    phone: str = Field(..., description='The user phone')


UserWithOptionalContacts = Union[UserWithContacts, UserPublic]


class User(UserWithContacts):
    login_id: str = Field(..., description='The user login identifier')
    login_type: EnumLoginService = Field(..., description='The user login service type')
    created_at: datetime = Field(..., description='The user created datetime')
    updated_at: datetime = Field(..., description='The user updated datetime')


class AuthGrantType(str, Enum):
    authorization_code = 'authorization_code'
    refresh_token = 'refresh_token'


class AccessToken(BaseModel):
    access_token: str = Field(..., descriprion='The access token')
    refresh_token: str = Field(None, descriprion='The refresh token')
    expires_in: int = Field(None, description='The token expires in')
    user: User = Field(..., description='The user related to access token')


class StorageCreateMe(TrimModel):
    name: str = Field(..., description='The storage name')
    latitude: float = Field(..., description='The storage latitude')
    longitude: float = Field(..., description='The storage longitude')
    address: str = Field(..., description='The storage address')


class StorageCreate(StorageCreateMe):
    user_id: int = Field(..., description='The storage user owner unique identifier', gt=0)


class StorageUpdateMe(TrimModel):
    storage_id: int = Field(..., description='The storage unique identifier', gt=0)
    name: str = Field(None, description='The storage name')
    latitude: float = Field(None, description='The storage latitude')
    longitude: float = Field(None, description='The storage longitude')
    address: str = Field(None, description='The storage address')


class StorageUpdate(StorageUpdateMe):
    pass


class Storage(StorageCreate):
    storage_id: int = Field(..., description='The storage unique identifier', gt=0)
    created_at: datetime = Field(..., description='The storage created datetime')
    updated_at: datetime = Field(..., description='The storage updated datetime')

    class Config(TrimModel.Config):
        orm_mode = True


class ItemCreate(TrimModel):
    storage_id: int = Field(..., description='The item storage unique identifier', gt=0)
    name_ru: str = Field(..., description='The item name in Russian', max_length=127)
    name_en: str = Field(..., description='The item name in English', max_length=127)
    desc_ru: str = Field(..., description='The item description in Russian', max_length=511)
    desc_en: str = Field(..., description='The item description in English', max_length=511)
    count: int = Field(..., description='The amount of this item in storage', ge=1)


class ItemUpdate(TrimModel):
    item_id: int = Field(..., description='The item unique identifier', gt=0)
    storage_id: int = Field(None, description='The item storage unique identifier', gt=0)
    name_ru: str = Field(None, description='The item name in Russian', max_length=127)
    name_en: str = Field(None, description='The item name in English', max_length=127)
    desc_ru: str = Field(None, description='The item description in Russian', max_length=511)
    desc_en: str = Field(None, description='The item description in English', max_length=511)
    count: int = Field(None, description='The amount of this item in storage', ge=1)


class ItemPublic(TrimModel):
    owner: UserPublic = Field(..., description='The item owner')
    item_id: int = Field(..., description='The item unique identifier', gt=0)
    name_ru: str = Field(..., description='The item name in Russian', max_length=127)
    name_en: str = Field(..., description='The item name in English', max_length=127)
    desc_ru: str = Field(..., description='The item description in Russian', max_length=511)
    desc_en: str = Field(..., description='The item description in English', max_length=511)
    count: int = Field(..., description='The amount of this item in storage', ge=1)
    remaining_count: int = Field(..., description='The remaining amount of this item in storage', gt=0)

    class Config(TrimModel.Config):
        orm_mode = True


class Item(ItemCreate):
    item_id: int = Field(..., description='The item unique identifier', gt=0)
    remaining_count: int = Field(..., description='The remaining amount of this item in storage', gt=0)
    created_at: datetime = Field(..., description='The item created datetime')
    updated_at: datetime = Field(..., description='The item updated datetime')

    class Config(TrimModel.Config):
        orm_mode = True


class ItemRequested(ItemPublic):
    owner: UserWithOptionalContacts = Field(..., description='The item owner')


class RequestCreateMe(TrimModel):
    item_id: int = Field(..., description='The item unique identifier', gt=0)
    count: int = Field(..., description='The amount of requested item', ge=1)
    rent_starts_at: datetime = Field(..., description='When the item rent starts')
    rent_ends_at: datetime = Field(..., description='When the item rent ends')


class RequestCreate(RequestCreateMe):
    user_id: int = Field(..., description='The requester unique identifier', gt=0)


class EnumRequestStatusUpdate(str, Enum):
    BOOKED = 'BOOKED'
    CANCELED = 'CANCELED'
    COMPLETED = 'COMPLETED'
    DELAYED = 'DELAYED'
    DENIED = 'DENIED'
    LENT = 'LENT'


class RequestUpdateMe(TrimModel):
    request_id: int = Field(..., description='The request unique identifier', gt=0)
    status: EnumRequestStatusUpdate = Field(..., description='The request status')


class RequestUpdate(TrimModel):
    request_id: int = Field(..., description='The request unique identifier', gt=0)
    status: EnumRequestStatusUpdate = Field(None, description='The request status')


class RequestCommon(TrimModel):
    request_id: int = Field(..., description='The request unique identifier', gt=0)
    count: int = Field(..., description='The amount of requested item', ge=1)
    rent_starts_at: datetime = Field(..., description='When the item rent starts')
    rent_ends_at: datetime = Field(..., description='When the item rent ends')
    status: EnumRequestStatus = Field(..., description='The request status')
    created_at: datetime = Field(..., description='The request created datetime')
    updated_at: datetime = Field(..., description='The request updated datetime')

    class Config(TrimModel.Config):
        orm_mode = True


class RequestMe(RequestCommon):
    item: ItemRequested = Field(..., description='The requested item')
    user_id: int = Field(..., description='The item requester unique identifier')


class RequestMeList(TrimModel):
    __root__: List[RequestMe]

    class Config(TrimModel.Config):
        orm_mode = True


class RequestItem(RequestCommon):
    item: Item = Field(..., description='The requested item')
    requester: UserWithOptionalContacts = Field(..., description='The item requester')


class RequestItemList(TrimModel):
    __root__: List[RequestItem]

    class Config(TrimModel.Config):
        orm_mode = True


class Request(RequestCommon):
    item_id: int = Field(..., description='The item unique identifier', gt=0)
    user_id: int = Field(..., description='The requester unique identifier', gt=0)
    notification_sent_at: datetime = Field(None, description='The notification sent datetime')
