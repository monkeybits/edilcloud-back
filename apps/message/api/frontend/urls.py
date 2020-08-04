# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import tracker_views

user_urlpatterns = []

generic_urlpatterns = []

tracker_urlpatterns = [
    url(
        r'^message/$',
        tracker_views.TrackerMessageListView.as_view(),
        name='tracker_message_list'
    ),
    url(
        r'^message/(?P<type>(project|company|profile){1})/(?P<pk>[0-9]+)/add/$',
        tracker_views.TrackerMessageAddView.as_view(),
        name='tracker_message_add'
    ),
    url(
        r'^message/(?P<pk>\d+)/$',
        tracker_views.TrackerMessageDetailView.as_view(),
        name='tracker_message_detail'
    ),
    url(
        r'^message/delete/(?P<pk>\d+)/$',
        tracker_views.TrackerMessageDeleteView.as_view(),
        name='tracker_message_delete'
    ),
    url(
        r'^talk/$',
        tracker_views.TrackerTalkListView.as_view(),
        name='tracker_talk_list'
    ),
    url(
        r'^talk/(?P<pk>\d+)/$',
        tracker_views.TrackerTalkDetailView.as_view(),
        name='tracker_talk_detail'
    ),
    url(
        r'^talk/delete/(?P<pk>\d+)/$',
        tracker_views.TrackerTalkDeleteView.as_view(),
        name='tracker_talk_delete'
    ),
]

urlpatterns = user_urlpatterns + generic_urlpatterns + tracker_urlpatterns
