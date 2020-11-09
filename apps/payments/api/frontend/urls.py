# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import tracker_views, generic_views

user_urlpatterns = []

generic_urlpatterns = []

tracker_urlpatterns = [
    url(
        r'^plans/$',
        generic_views.GenericPlansViews.as_view(),
        name='generic_view_plans'
    ),
    url(
        r'^checkout/$',
        generic_views.GenericCheckoutSessionView.as_view(),
        name='generic_view_pay_checkout'
    ),
]

urlpatterns = user_urlpatterns + generic_urlpatterns + tracker_urlpatterns
