from fastapi.routing import APIRouter

from .. import schemas
from ..utils import get_version as get_version_


router = APIRouter(prefix='', tags=['default'])


@router.get(
    '/version',
    response_model=schemas.Version
)
def get_version():
    """Get number of version"""
    return {'version': get_version_()}
