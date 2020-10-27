# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from admin_tools.menu import items
from jmb.core.admin.menu import register_menu

currency_menu_item = items.MenuItem(
    _('message'),
    reverse('admin:app_list', kwargs={'app_label': 'message'}),
    children=[items.MenuItem(_('add message'), reverse('admin:message_message_add', )),
              items.MenuItem(_('list message'), reverse('admin:message_message_changelist', )),
              ]
)

register_menu(currency_menu_item, 'message')
