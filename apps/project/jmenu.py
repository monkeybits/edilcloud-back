# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from admin_tools.menu import items
from jmb.core.admin.menu import register_menu

currency_menu_item = items.MenuItem(
    _('project'),
    reverse('admin:app_list', kwargs={'app_label': 'project'}),
    children=[
        items.MenuItem(_('add project'), reverse('admin:project_project_add', )),
        items.MenuItem(_('list project'), reverse('admin:project_project_changelist', )),
        items.MenuItem(_('add task'), reverse('admin:project_task_add', )),
        items.MenuItem(_('list task'), reverse('admin:project_task_changelist', )),
    ]
)

register_menu(currency_menu_item, 'project')
