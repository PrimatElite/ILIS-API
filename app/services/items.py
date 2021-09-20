from .base import DictStrAny, Session
from .searchable import Searchable
from .storages import Storages
from ..exceptions import StorageNotFoundError
from ..models import ORMItems


class Items(Searchable):
    model = ORMItems

    fields_to_update = [ORMItems.storage_id, ORMItems.name_ru, ORMItems.name_en, ORMItems.desc_ru, ORMItems.desc_en,
                        ORMItems.count]
    simple_fields_to_update = [ORMItems.name_ru, ORMItems.name_en, ORMItems.desc_ru, ORMItems.desc_en]

    @classmethod
    def _check_creation(cls, db: Session, data: DictStrAny):
        storage = Storages.get_by_id(db, data['storage_id'])
        if storage is None:
            raise StorageNotFoundError(data['storage_id'])

    @classmethod
    def _update_complicated_fields(cls, db: Session, obj: ORMItems, data: DictStrAny) -> ORMItems:
        if data.get('storage_id') is not None:
            dest_storage = Storages.get_by_id(db, data['storage_id'])
            if dest_storage is not None and obj.storage.user_id == dest_storage.user_id:
                obj.storage_id = data['storage_id']
        if data.get('count') is not None and data['count'] >= obj.count - obj.remaining_count:
            obj.count = data['count']
        return obj
