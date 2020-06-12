# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ProfileConfig(AppConfig):
    name = 'apps.profile'
    label = 'profile'
    verbose_name = _('Profile')

    def ready(self):
        from . import signals
