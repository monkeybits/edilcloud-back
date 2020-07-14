# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.media.api.frontend.views import generic_views
from .views import tracker_views

user_urlpatterns = []

generic_urlpatterns = []

tracker_urlpatterns = [
    url(
        r'^photo/(?P<pk>\d+)/$',
        tracker_views.TrackerPhotoDetailView.as_view(),
        name='tracker_photo_detail'
    ),
    url(
        r'^photo/(?P<type>(project|company|bom){1})/(?P<pk>[0-9]+)/add/$',
        tracker_views.TrackerPhotoAddView.as_view(),
        name='tracker_photo_add'
    ),
    url(
        r'^photo/edit/(?P<pk>\d+)/$',
        tracker_views.TrackerPhotoEditView.as_view(),
        name='tracker_photo_edit'
    ),
    url(
        r'^photo/delete/(?P<pk>\d+)/$',
        tracker_views.TrackerPhotoDeleteView.as_view(),
        name='tracker_photo_delete'
    ),
    url(
        r'^photo/download/(?P<pk>\d+)/$',
        tracker_views.TrackerPhotoDownloadView.as_view(),
        name='tracker_photo_download'
    ),
    url(
        r'^video/(?P<pk>\d+)/$',
        tracker_views.TrackerVideoDetailView.as_view(),
        name='tracker_video_detail'
    ),
    url(
        r'^video/(?P<type>(project|company|bom){1})/(?P<pk>[0-9]+)/add/$',
        tracker_views.TrackerVideoAddView.as_view(),
        name='tracker_video_add'
    ),
    url(
        r'^video/edit/(?P<pk>\d+)/$',
        tracker_views.TrackerVideoEditView.as_view(),
        name='tracker_video_edit'
    ),
    url(
        r'^video/delete/(?P<pk>\d+)/$',
        tracker_views.TrackerVideoDeleteView.as_view(),
        name='tracker_video_delete'
    ),
    url(
        r'^video/download/(?P<pk>\d+)/$',
        tracker_views.TrackerVideoDownloadView.as_view(),
        name='tracker_video_download'
    ),
    url(
        r'^video/download/(?P<pk>\d+)/public/$',
        generic_views.PublicVideoDownloadView.as_view(),
        name='public_video_download'
    ),
    url(
        r'^files/download/(?P<pk>\d+)/public/$',
        generic_views.PublicVideoDownloadView.as_view(),
        name='public_video_download'
    )
]

urlpatterns = user_urlpatterns + generic_urlpatterns + tracker_urlpatterns
