# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from admin_tools.menu import items
from jmb.core.admin.menu import register_menu

currency_menu_item = items.MenuItem(
    _('notify'),
    reverse('admin:app_list', kwargs={'app_label': 'notify'}),
    children=[items.MenuItem(_('add notify'), reverse('admin:notify_notify_add', )),
              items.MenuItem(_('list notify'), reverse('admin:notify_notify_changelist', )),
              ]
)

register_menu(currency_menu_item, 'notify')
