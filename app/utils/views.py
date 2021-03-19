from flask_admin.contrib.sqla.fields import QuerySelectField as QuerySelectField_


class QuerySelectField(QuerySelectField_):
    def populate_obj(self, obj, name):
        """
        Populates `obj.<name>` with the field's data.

        :note: This is a destructive operation. If `obj.<name>` already exists,
               it will be overridden. Use with caution.
        """
        setattr(obj, name, getattr(self.data, name))
