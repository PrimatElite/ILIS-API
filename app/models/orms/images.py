from sqlalchemy import Column, Integer, String
from typing import Union

from .base import Base
from ..db import seq


class Images(Base):
    __tablename__ = 'images'

    image_id = Column(Integer, seq, primary_key=True)
    item_id = Column(Integer, nullable=False)
    path = Column(String, nullable=False)

    @classmethod
    def get_images(cls):
        return [cls.orm2dict(image) for image in cls.query.order_by(cls.image_id).all()]

    @classmethod
    def get_images_by_item(cls, item_id: int):
        return [cls.orm2dict(image) for image in cls.query.filter_by(item_id=item_id).order_by(cls.image_id).all()]

    @classmethod
    def get_image_by_id(cls, image_id: int):
        return cls.orm2dict(cls.query.filter_by(image_id=image_id).first())

    get_obj_by_id = get_image_by_id

    @classmethod
    def get_image_by_name(cls, image_name: int):
        return cls.orm2dict(cls.query.filter_by(path=image_name).first())

    @classmethod
    def create(cls, data: dict) -> Union[dict, None]:
        from .items import Items

        item_dict = Items.get_item_by_id(data['item_id'])
        if item_dict is not None:
            image = cls.dict2cls(data, False).add()
            image_dict = cls.orm2dict(image)
            return image_dict
        return None

    @classmethod
    def delete_images_by_item(cls, item_id: int):
        for image_dict in cls.get_images_by_item(item_id):
            cls._delete(image_dict)
