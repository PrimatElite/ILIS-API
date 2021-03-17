from flask_restplus import fields, Namespace

from ..models.enums import EnumLoginService, EnumUserRole


class DefaultModels:
    api = Namespace('default', description='Default operations')
    version = api.model('version', {
        'version': fields.String(required=True, description='The number of version')
    })


class UsersModels:
    api = Namespace('users', description='Users operations')
    create_user = api.model('create_user', {
        'login_id': fields.String(required=True, description='The user login identifier'),
        'login_type': fields.String(required=True, description='The user login service type',
                                    enum=list(EnumLoginService.__members__)),
        'name': fields.String(description='The user name'),
        'surname': fields.String(description='The user surname'),
        'role': fields.String(required=True, description='The user role', enum=list(EnumUserRole.__members__)),
        'email': fields.String(description='The user email'),
        'phone': fields.String(description='The user phone'),
        'avatar': fields.String(description='The user avatar')
    })
    update_user_me = api.model('update_user_me', {
        'name': fields.String(description='The user name'),
        'surname': fields.String(description='The user surname'),
        'email': fields.String(description='The user email'),
        'phone': fields.String(description='The user phone')
    })
    update_user = api.clone('update_user', {
        'user_id': fields.Integer(required=True, description='The user identifier'),
        'role': fields.String(description='The user role', enum=list(EnumUserRole.__members__))
    }, update_user_me)
    user_public = api.model('user_public', {
        'user_id': fields.Integer(required=True, description='The user identifier'),
        'name': fields.String(required=True, description='The user name'),
        'surname': fields.String(required=True, description='The user surname'),
        'role': fields.String(required=True, description='The user role', enum=list(EnumUserRole.__members__)),
        'avatar': fields.String(required=True, description='The user avatar')
    })
    user_with_contacts = api.clone('user_with_contacts', user_public, {
        'email': fields.String(required=True, description='The user email'),
        'phone': fields.String(required=True, description='The user phone')
    })
    user = api.clone('user', user_with_contacts, {
        'login_id': fields.String(required=True, description='The user login identifier'),
        'login_type': fields.String(required=True, description='The user login service type',
                                    enum=list(EnumLoginService.__members__)),
        'created_at': fields.DateTime(required=True, description='The user created datetime'),
        'updated_at': fields.DateTime(required=True, description='The user updated datetime')
    })


class StoragesModels:
    api = Namespace('storages', description='Storages operations')
    create_storage_me = api.model('create_storage_me', {
        'name': fields.String(required=True, description='The storage name'),
        'latitude': fields.Float(required=True, description='The storage latitude'),
        'longitude': fields.Float(required=True, description='The storage longitude'),
        'address': fields.String(required=True, description='The storage address')
    })
    create_storage = api.clone('create_storage', create_storage_me, {
        'user_id': fields.Integer(required=True, description='The storage user owner'),
    })
    update_storage_me = api.model('update_storage_me', {
        'storage_id': fields.Integer(required=True, description='The storage unique identifier'),
        'name': fields.String(description='The storage name'),
        'latitude': fields.Float(description='The storage latitude'),
        'longitude': fields.Float(description='The storage longitude'),
        'address': fields.String(description='The storage address')
    })
    update_storage = api.clone('update_storage', update_storage_me)
    storage = api.clone('storage', {
        'storage_id': fields.Integer(required=True, description='The storage unique identifier')
    }, create_storage)


class ItemsModels:
    api = Namespace('items', description='Items operations')
    create_item = api.model('create_item', {
        'storage_id': fields.Integer(required=True, description='The item storage'),
        'name_ru': fields.String(required=True, max_length=127, description='The item name in Russian'),
        'name_en': fields.String(required=True, max_length=127, description='The item name in English'),
        'desc_ru': fields.String(required=True, max_length=511, description='The item description in Russian'),
        'desc_en': fields.String(required=True, max_length=511, description='The item description in English'),
        'count': fields.Integer(required=True, min=1, description='The amount of this item in storage')
    })
    update_item = api.model('update_item', {
        'item_id': fields.Integer(required=True, description='The item identifier'),
        'storage_id': fields.Integer(description='The item storage'),
        'name_ru': fields.String(max_length=127, description='The item name in Russian'),
        'name_en': fields.String(max_length=127, description='The item name in English'),
        'desc_ru': fields.String(max_length=511, description='The item description in Russian'),
        'desc_en': fields.String(max_length=511, description='The item description in English'),
        'count': fields.Integer(min=1, description='The amount of this item in storage')
    })
    search_items = api.parser()
    search_items.add_argument('content', type=str, required=True, help='Write items you require')
    item_public = api.clone('item_public', {
        'owner': fields.Nested(UsersModels.user_public, required=True, description='The item owner'),
        'item_id': fields.Integer(required=True, description='The item identifier'),
        'name_ru': fields.String(required=True, max_length=127, description='The item name in Russian'),
        'name_en': fields.String(required=True, max_length=127, description='The item name in English'),
        'desc_ru': fields.String(required=True, max_length=511, description='The item description in Russian'),
        'desc_en': fields.String(required=True, max_length=511, description='The item description in English'),
        'count': fields.Integer(required=True, min=1, description='The amount of this item in storage')
    })
    item = api.clone('item', {
        'item_id': fields.Integer(required=True, description='The item identifier')
    }, create_item, {
        'created_at': fields.DateTime(required=True, description='The item created datetime'),
        'updated_at': fields.DateTime(required=True, description='The item updated datetime')
    })


class AuthModels:
    api = Namespace('auth', description='Auth operations')
    access_token = api.model('access_token', {
        'access_token': fields.String(required=True, descriprion='The access token'),
        'refresh_token': fields.String(descriprion='The refresh token'),
        'expires_in': fields.Integer(description='The token expires in'),
        'user': fields.Nested(UsersModels.user, required=True, description='The user related to access token')
    })
