from flask_admin.contrib.sqla.fields import QuerySelectField as QuerySelectField_

from ..models import Users


def get_user_label(user: Users) -> str:
    label = f'{user.user_id}'
    for value in [user.name, user.surname]:
        if value is not None:
            label += f' {value}'
    return label


class QuerySelectField(QuerySelectField_):
    def populate_obj(self, obj, name):
        """
        Populates `obj.<name>` with the field's data.
        """
        setattr(obj, name, getattr(self.data, name))
