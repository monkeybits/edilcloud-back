# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _


NOTIFY_NOTIFY_EVENT_CHOICES = (
    ('mr', _('received message'),),
)
NOTIFY_NOTIFY_NO_REPLY_EMAIL = 'notification@edilcloud.io'
NOTIFY_NOTIFY_SEND_NOTIFICATION_ENABLED = True

NOTIFY_CONTENT_TYPE_LIMIT_CHOICES_TO = [
    {'app_label': 'profile', 'model': 'company'},
    {'app_label': 'profile', 'model': 'profile'},
    {'app_label': 'profile', 'model': 'partnership'},
    {'app_label': 'profile', 'model': 'favourite'},
    {'app_label': 'project', 'model': 'project'},
    {'app_label': 'project', 'model': 'team'},
    {'app_label': 'project', 'model': 'task'},
    {'app_label': 'project', 'model': 'activity'},
    {'app_label': 'quotation', 'model': 'offer'},
    {'app_label': 'quotation', 'model': 'bom'},
]
