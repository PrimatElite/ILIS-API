from flask import current_app, flash, redirect, Response
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import BaseForm
from flask_login import login_url
from math import ceil
from sqlalchemy.orm.scoping import scoped_session
from typing import List, Tuple, Type

from ..login import is_user_authenticated
from ...models.orms.base import Base


class BaseView(ModelView):
    column_display_pk = True

    can_set_page_size = True

    form_excluded_columns = ['created_at', 'updated_at']

    extra_columns = []

    def __init__(self, model: Type[Base], session: scoped_session, **kwargs):
        super(BaseView, self).__init__(model, session, **kwargs)

    def is_accessible(self) -> bool:
        return is_user_authenticated()

    def inaccessible_callback(self, name: str, **kwargs) -> Response:
        flash('Please, log in', 'error')
        return redirect(login_url(current_app.login_manager.login_view))

    def after_model_change(self, form: Type[BaseForm], model: Type[Base], is_created: bool):
        if is_created:
            self.model.after_create(self.model.orm2dict(model))
        else:
            self.model.after_update(self.model.orm2dict(model))

    def on_model_delete(self, model: Type[Base]):
        if not self.model.can_delete(self.model.orm2dict(model)):
            raise Exception(f'{self.model.__name__[:-1]} {getattr(model, self.model.get_id_name())} can\'t be deleted')

    def after_model_delete(self, model: Type[Base]):
        self.model.after_delete(self.model.orm2dict(model))

    def get_column_names(self, only_columns: List[str], excluded_columns: List[str]) -> List[Tuple[str, str]]:
        only_columns += self.extra_columns
        return super().get_column_names(only_columns, excluded_columns)

    @expose('/')
    def index_view(self):
        if self.can_delete:
            delete_form = self.delete_form()
        else:
            delete_form = None

        # Grab parameters from URL
        view_args = self._get_list_extra_args()

        # Map column index to column name
        sort_column = self._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]

        # Get page size
        page_size = view_args.page_size or self.page_size

        # Get count and data
        count, data = self.get_list(view_args.page, sort_column, view_args.sort_desc,
                                    view_args.search, view_args.filters, page_size=page_size)

        list_forms = {}
        if self.column_editable_list:
            for row in data:
                list_forms[self.get_pk_value(row)] = self.list_form(obj=row)

        # Calculate number of pages
        if count is not None and page_size:
            num_pages = int(ceil(count / float(page_size)))
        elif not page_size:
            num_pages = 0  # hide pager for unlimited page_size
        else:
            num_pages = None  # use simple pager

        # Various URL generation helpers
        def pager_url(p):
            # Do not add page number if it is first page
            if p == 0:
                p = None

            return self._get_list_url(view_args.clone(page=p))

        def sort_url(column, invert=False, desc=None):
            if not desc and invert and not view_args.sort_desc:
                desc = 1

            return self._get_list_url(view_args.clone(sort=column, sort_desc=desc))

        def unsort_url():
            return self._get_list_url(view_args.clone(sort=None, sort_desc=None))

        def page_size_url(s):
            if not s:
                s = self.page_size

            return self._get_list_url(view_args.clone(page_size=s))

        # Actions
        actions, actions_confirmation = self.get_actions_list()
        if actions:
            action_form = self.action_form()
        else:
            action_form = None

        clear_search_url = self._get_list_url(view_args.clone(page=0,
                                                              sort=view_args.sort,
                                                              sort_desc=view_args.sort_desc,
                                                              search=None,
                                                              filters=None))

        return self.render(
            self.list_template,
            data=data,
            list_forms=list_forms,
            delete_form=delete_form,
            action_form=action_form,

            # List
            list_columns=self._list_columns,
            sortable_columns=self._sortable_columns,
            editable_columns=self.column_editable_list,
            list_row_actions=self.get_list_row_actions(),

            # Pagination
            count=count,
            pager_url=pager_url,
            num_pages=num_pages,
            can_set_page_size=self.can_set_page_size,
            page_size_url=page_size_url,
            page=view_args.page,
            page_size=page_size,
            default_page_size=self.page_size,

            # Sorting
            sort_column=view_args.sort,
            sort_desc=view_args.sort_desc,
            sort_url=sort_url,
            unsort_url=unsort_url,

            # Search
            search_supported=self._search_supported,
            clear_search_url=clear_search_url,
            search=view_args.search,
            search_placeholder=self.search_placeholder(),

            # Filters
            filters=self._filters,
            filter_groups=self._get_filter_groups(),
            active_filters=view_args.filters,
            filter_args=self._get_filters(view_args.filters),

            # Actions
            actions=actions,
            actions_confirmation=actions_confirmation,

            # Misc
            enumerate=enumerate,
            get_pk_value=self.get_pk_value,
            get_value=self.get_list_value,
            return_url=self._get_list_url(view_args),

            # Extras
            extra_args=view_args.extra_args,
        )
