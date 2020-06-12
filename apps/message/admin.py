# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext as _

from web.core.admin import UserAdminMixin
from . import models


class MessageInlineAdmin(admin.TabularInline):
    model = models.Message
    extra = 0
    exclude = (
        'creator', 'last_modifier', 'date_create',
        'date_last_modify', 'ordering',
    )
    raw_id_fields = ('talk', 'sender',)


class TalkAdmin(UserAdminMixin, admin.ModelAdmin):
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'code', 'content_type', 'object_id',
                'for_concrete_model',
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
    inlines = (MessageInlineAdmin,)
    list_display = (
        'id', 'status', 'code', 'get_messages_count',
        'content_type', 'content_object', 'object_id', 'for_concrete_model',
    )
    readonly_fields = (
        'code', 'creator', 'date_create',
        'last_modifier', 'date_last_modify',
    )
    list_editable = ('status',)
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE
    show_full_result_count = False


class MessageAdmin(UserAdminMixin, admin.ModelAdmin):
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'body', 'talk', 'sender',
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
        'id', 'status', 'body',
        'sender', 'talk',
    )
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    list_editable = ('status',)
    raw_id_fields = ('sender',)
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE
    show_full_result_count = False


admin.site.register(models.Talk, TalkAdmin)
admin.site.register(models.Message, MessageAdmin)
