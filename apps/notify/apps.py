# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class NotifyConfig(AppConfig):
    name = 'apps.notify'
    label = 'notify'
    verbose_name = _('Notify')

    def ready(self):
        from . import signals