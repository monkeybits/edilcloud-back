# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

PROJECT_PROJECT_INTERNAL = 'i'
PROJECT_PROJECT_SHARED = 's'

PROJECT_ACTIVITY_TODO = 'to-do'
PROJECT_ACTIVITY_PROGRESS = 'progress'
PROJECT_ACTIVITY_COMPLETED = 'completed'

PROJECT_PROJECT_TYPOLOGY_CHOICES = (
    (PROJECT_PROJECT_INTERNAL, _('internal')),
    (PROJECT_PROJECT_SHARED, _('shared')),
)

PROJECT_ACTIVITY_STATUS_CHOICES = (
    (PROJECT_ACTIVITY_TODO, _('to-do')),
    (PROJECT_ACTIVITY_PROGRESS, _('progress')),
    (PROJECT_ACTIVITY_COMPLETED, _('completed')),
)

PROJECT_PROJECT_STATUS_CHOICES = (
    (0, _('closed')),
    (1, _('open')),
    (-1, _('draft')),
)

PROJECT_TEAM_ROLE_CHOICES = (
    (settings.OWNER, _('owner'),),
    (settings.DELEGATE, _('delegate'),),
    (settings.LEVEL_1, _('level 1'),),
    (settings.LEVEL_2, _('level 2'),),
)
