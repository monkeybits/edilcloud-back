# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import tracker_views, generic_views

user_urlpatterns = []

generic_urlpatterns = []

tracker_urlpatterns = [
    url(
        r'^plans/$',
        generic_views.GenericPlansViews.as_view(),
        name='tracker_document_detail'
    )
]

urlpatterns = user_urlpatterns + generic_urlpatterns + tracker_urlpatterns
