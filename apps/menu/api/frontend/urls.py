# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import user_views


user_urlpatterns = [
    url(
        r'^menu/$',
        user_views.MenuListView.as_view(),
        name='menu_list'
    ),
]

generic_urlpatterns = []

tracker_urlpatterns = []

urlpatterns = user_urlpatterns + generic_urlpatterns + tracker_urlpatterns
