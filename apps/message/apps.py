# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class MessageConfig(AppConfig):
    name = 'apps.message'
    label = 'message'
    verbose_name = _('Message')

    def ready(self):
        from . import signals
