# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class MediaConfig(AppConfig):
    name = 'apps.media'
    label = 'media'
    verbose_name = _('Media')

    def ready(self):
        from . import signals
