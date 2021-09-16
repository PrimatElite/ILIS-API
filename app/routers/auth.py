from fastapi import Depends, status, Query
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from .. import schemas
from ..cruds import CRUDUsers
from ..dependencies import get_db
from ..models import EnumLoginService, EnumUserRole
from ..oauth2 import get_service


router = APIRouter(prefix='/auth', tags=['auth'])


@router.get(
    '/code',
    response_class=RedirectResponse,
    response_description='Redirect to page with code',
    status_code=303
)
def get_code_url(
        service: EnumLoginService = Query(..., description='The login service'),
        redirect_uri: str = Query(..., description='The redirect uri')
):
    """Redirect to page with code"""
    return RedirectResponse(get_service(service.value).get_code_url(redirect_uri), status.HTTP_303_SEE_OTHER)


@router.post(
    '/token',
    response_model=schemas.AccessToken,
    responses={
        200: {'description': 'Success'},
        501: {'description': 'Not implemented'}
    }
)
def get_token(
        service: EnumLoginService = Query(..., description='The login service'),
        grant_type: schemas.AuthGrantType = Query(..., description='The grant type'),
        code: str = Query(None, description='The authorization code'),
        redirect_uri: str = Query(None, description='The redirect uri'),
        refresh_token: str = Query(None, description='The refresh token'),
        db: Session = Depends(get_db)
):
    """Get access token"""
    service_name = service.value
    service = get_service(service_name)

    token_response, user_info = None, None
    # try:
    if grant_type == schemas.AuthGrantType.authorization_code:
        token_response, user_info = service.get_access_token(code, redirect_uri)
    else:
        token_response, user_info = service.get_refresh_token(refresh_token)
    # except KeyError as e:  # TODO
    #     help_ = list(filter(lambda arg: arg.name == e.args[0], _token_parser.args))[0].help
    #     errors = {e.args[0]: f'{help_} Missing required parameter in the query string'}
    #     api.abort(HTTPStatus.BAD_REQUEST, 'Input payload validation failed', errors=errors)

    user = CRUDUsers.get_user_by_login(db, service.get_id_from_info(user_info), service_name)

    if user is None:
        data = service.transform_info(user_info)
        data['role'] = EnumUserRole.USER
        user = CRUDUsers.create(db, data)

    access_token, refresh_token, expires_in = token_response
    return {'access_token': access_token, 'refresh_token': refresh_token, 'expires_in': expires_in, 'user': user}
