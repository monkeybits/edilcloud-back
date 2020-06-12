# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from admin_tools.menu import items
from jmb.core.admin.menu import register_menu

currency_menu_item = items.MenuItem(
    _('menu'),
    reverse('admin:app_list', kwargs={'app_label': 'menu'}),
    children=[items.MenuItem(_('add menu'), reverse('admin:menu_menu_add', )),
              items.MenuItem(_('list menu'), reverse('admin:menu_menu_changelist', )),
              ]
)

register_menu(currency_menu_item, 'menu')
