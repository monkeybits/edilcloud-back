# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext as _

from web.core.admin import UserAdminMixin
from . import models


class DocumentAdmin(UserAdminMixin, admin.ModelAdmin):
    fieldsets = (
        (_('general_information'), {
           'fields': (
               'title', 'description', 'document',
               'content_type', 'object_id', 'for_concrete_model',
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
        'id', 'status', 'title', 'is_public',
        'description', 'document', 'content_type',
        'content_object', 'for_concrete_model', 'object_id'
    )
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    list_editable = ('status',)


admin.site.register(models.Document, DocumentAdmin)
