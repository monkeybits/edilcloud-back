# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import tracker_views

user_urlpatterns = []

generic_urlpatterns = []

tracker_urlpatterns = [
    url(
        r'^notification/recipient/count/$',
        tracker_views.TrackerNotificationRecipientCountDetailView.as_view(),
        name='tracker_notification_recipient_count_detail'
    ),
    url(
        r'^notification/recipient/(?P<type>(new|read|trash){1})_list/$',
        tracker_views.TrackerNotificationRecipientListView.as_view(),
        name='tracker_notification_recipient_list'
    ),
    url(
        r'^notification/recipient/event/(?P<type>(profile|company|offer|project|task|activity|team|bom|message|partnership|favourite){1})/list/$',
        tracker_views.TrackerNotificationRecipientEventListView.as_view(),
        name='tracker_notification_recipient_event_list'
    ),
    url(
        r'^notification/read/(?P<pk>\d+)/$',
        tracker_views.TrackerNotificationRecipientReadView.as_view(),
        name='tracker_notification_recipient_read'
    ),
    url(
        r'^notification/delete/(?P<pk>\d+)/$',
        tracker_views.TrackerNotificationDeleteView.as_view(),
        name='tracker_notification_delete'
    ),
    url(
        r'^notification/read/all/$',
        tracker_views.TrackerNotificationRecipientReadAllView.as_view(),
        name='tracker_notification_recipient_read'
    ),
]

urlpatterns = user_urlpatterns + generic_urlpatterns + tracker_urlpatterns
