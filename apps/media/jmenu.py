# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from admin_tools.menu import items
from jmb.core.admin.menu import register_menu

currency_menu_item = items.MenuItem(
    _('media'),
    reverse('admin:app_list', kwargs={'app_label': 'media'}),
    children=[items.MenuItem(_('add photo'), reverse('admin:media_photo_add', )),
        items.MenuItem(_('list photo'), reverse('admin:media_photo_changelist', )),
        items.MenuItem(_('add video'), reverse('admin:media_video_add', )),
        items.MenuItem(_('list video'), reverse('admin:media_video_changelist', )),
    ]
)

register_menu(currency_menu_item, 'media')
