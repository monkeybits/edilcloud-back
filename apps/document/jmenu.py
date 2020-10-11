# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from admin_tools.menu import items
from jmb.core.admin.menu import register_menu

currency_menu_item = items.MenuItem(
    _('document'),
    reverse('admin:app_list', kwargs={'app_label': 'document'}),
    children=[
            items.MenuItem(_('add document'), reverse('admin:document_document_add', )),
            items.MenuItem(_('list document'), reverse('admin:document_document_changelist', )),
            ]
)

register_menu(currency_menu_item, 'document')
