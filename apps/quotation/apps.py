# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class QuotationConfig(AppConfig):
    name = 'apps.quotation'
    label = 'quotation'
    verbose_name = _('Quotation')

    def ready(self):
        from . import signals
