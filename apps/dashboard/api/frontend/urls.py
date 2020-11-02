# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import tracker_views

user_urlpatterns = []

generic_urlpatterns = []

tracker_urlpatterns = [
    url(
        r'^projects/$',
        tracker_views.TrackerProjectsListView.as_view(),
        name='tracker_projects_detail'
    ),
]

urlpatterns = user_urlpatterns + generic_urlpatterns + tracker_urlpatterns
