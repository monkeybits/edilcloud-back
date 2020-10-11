# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ProjectConfig(AppConfig):
    name = 'apps.project'
    label = 'project'
    verbose_name = _('Project')

    def ready(self):
        from . import signals
