# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from admin_tools.menu import items
from jmb.core.admin.menu import register_menu

currency_menu_item = items.MenuItem(
    _('product'),
    reverse('admin:app_list', kwargs={'app_label': 'product'}),
    children=[items.MenuItem(_('add unit'), reverse('admin:product_unit_add', )),
              items.MenuItem(_('list unit'), reverse('admin:product_unit_changelist', )),
              items.MenuItem(_('add typology'), reverse('admin:product_typology_add', )),
              items.MenuItem(_('list typology'), reverse('admin:product_typology_changelist', )),
              items.MenuItem(_('add category'), reverse('admin:product_category_add', )),
              items.MenuItem(_('list category'), reverse('admin:product_category_changelist', )),
              items.MenuItem(_('add subcategory'), reverse('admin:product_subcategory_add', )),
              items.MenuItem(_('list subcategory'), reverse('admin:product_subcategory_changelist', )),
              items.MenuItem(_('add product'), reverse('admin:product_product_add', )),
              items.MenuItem(_('list product'), reverse('admin:product_product_changelist', )),
              ]
)

register_menu(currency_menu_item, 'product')
