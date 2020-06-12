# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from admin_tools.menu import items
from jmb.core.admin.menu import register_menu

currency_menu_item = items.MenuItem(
    _('quotation'),
    reverse('admin:app_list', kwargs={'app_label': 'quotation'}),
    children=[items.MenuItem(_('add bom'), reverse('admin:quotation_bom_add', )),
              items.MenuItem(_('list bom'), reverse('admin:quotation_bom_changelist', )),
              items.MenuItem(_('add bom row'), reverse('admin:quotation_bomrow_add', )),
              items.MenuItem(_('list bom row'), reverse('admin:quotation_bomrow_changelist', )),
              items.MenuItem(_('add quotation'), reverse('admin:quotation_quotation_add', )),
              items.MenuItem(_('list quotation'), reverse('admin:quotation_quotation_changelist', )),
              items.MenuItem(_('add quotation row'), reverse('admin:quotation_quotationrow_add', )),
              items.MenuItem(_('list quotation row'), reverse('admin:quotation_quotationrow_changelist', )),
              items.MenuItem(_('add offer'), reverse('admin:quotation_offer_add', )),
              items.MenuItem(_('list offer'), reverse('admin:quotation_offer_changelist', )),
              items.MenuItem(_('add certification'), reverse('admin:quotation_certification_add', )),
              items.MenuItem(_('list certification'), reverse('admin:quotation_certification_changelist', )),
              ]
)

register_menu(currency_menu_item, 'quotation')
