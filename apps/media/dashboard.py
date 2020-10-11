# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
import admin_tools
from admin_tools.dashboard import modules, AppIndexDashboard
from jmb.core.admin import dashboard as jmb_dashboard


class DefaultDashboard(modules.Group):
    def __init__(self, **kwargs):
        kwargs.update({
            'title': _("media"),
            'display': "tabs",
            'children': [Models()]
        })
        super(DefaultDashboard, self).__init__(**kwargs)


class MainDashboard(modules.Group):
    def __init__(self, **kwargs):
        kwargs.update({
            'title': _("media"),
            'display': "tabs",
            'children': [Models()]
        })
        super(MainDashboard, self).__init__(**kwargs)


class Models(modules.ModelList):
    def __init__(self, **kwargs):
        kwargs.update({
            'title': _("main models"),
            'models': ('media.models.Photo', 'media.models.Video',
                       ),
        })
        super(Models, self).__init__(**kwargs)


class DefaultAppDashboard(AppIndexDashboard):
    def __init__(self, app_title, models, **kwargs):
        AppIndexDashboard.__init__(self, app_title, models, **kwargs)
        self.columns = 3

    def init_with_context(self, context):
        self.children.append(DefaultDashboard(), )


jmb_dashboard.register_group(MainDashboard, 'media')
admin_tools.dashboard.register(DefaultAppDashboard, 'media')
