# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext as _

from web.core.admin import UserAdminMixin
from . import models


class MenuAdmin(UserAdminMixin, admin.ModelAdmin):
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'parent', 'name', 'title',
                'ui_sref', 'icon',
            )
        }),
        (_('visualization_admin'), {
            'classes': ('collapse',),
            'fields': ('ordering', 'status')
        }),
        (_('logs_admin'), {
            'classes': ('collapse',),
            'fields': (
                'creator', 'date_create', 'last_modifier',
                'date_last_modify',
            )
        }),
    )
    list_display = (
        'id', 'status', 'ordering',
        'parent', 'name', 'title',
        'ui_sref', 'icon',
    )
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    list_editable = ('status',)


admin.site.register(models.Menu, MenuAdmin)
