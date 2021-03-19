from flask_admin.contrib.sqla.fields import QuerySelectField as QuerySelectField_


class QuerySelectField(QuerySelectField_):
    def populate_obj(self, obj, name):
        """
        Populates `obj.<name>` with the field's data.
        """
        setattr(obj, name, getattr(self.data, name))
