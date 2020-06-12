# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext as _

from web.core.admin import UserAdminMixin
from . import models


class RecipientInlineAdmin(admin.TabularInline):
    model = models.Notify.recipients.through
    fields = (
        'recipient', 'is_email', 'is_notify',
        'is_email_sent' ,'reading_date', 'status'
    )
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    extra = 0
    verbose_name_plural = _('Notification Recipients')
    raw_id_fields = ('recipient',)


class NotifyAdmin(UserAdminMixin, admin.ModelAdmin):
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'sender', 'subject',
                'body', 'content_type', 'object_id'
            )
        }),
        (_('visualization_admin'), {
            'classes': ('collapse',),
            'fields': ('ordering',)
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
        'sender', 'subject', 'body',
        'content_type', 'object_id'
    )
    inlines = (RecipientInlineAdmin,)
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    raw_id_fields = ('sender',)


admin.site.register(models.Notify, NotifyAdmin)
