# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from admin_tools.menu import items
from jmb.core.admin.menu import register_menu

currency_menu_item = items.MenuItem(
    _('profile'),
    reverse('admin:app_list', kwargs={'app_label': 'profile'}),
    children=[
        items.MenuItem(_('add company'), reverse('admin:profile_company_add', )),
        items.MenuItem(_('list company'), reverse('admin:profile_company_changelist', )),
        items.MenuItem(_('add profile'), reverse('admin:profile_profile_add', )),
        items.MenuItem(_('list profile'), reverse('admin:profile_profile_changelist', )),
        items.MenuItem(_('add invite'), reverse('admin:profile_invite_add', )),
        items.MenuItem(_('list invite'), reverse('admin:profile_invite_changelist', )),
        items.MenuItem(_('add favourite'), reverse('admin:profile_favourite_add', )),
        items.MenuItem(_('list favourite'), reverse('admin:profile_favourite_changelist', )),
    ]
)

register_menu(currency_menu_item, 'profile')
