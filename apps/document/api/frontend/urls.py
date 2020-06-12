# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import tracker_views

user_urlpatterns = []

generic_urlpatterns = []

tracker_urlpatterns = [
    url(
        r'^document/(?P<pk>\d+)/$',
        tracker_views.TrackerDocumentDetailView.as_view(),
        name='tracker_document_detail'
    ),
    url(
        r'^document/(?P<type>(company|bom|profile){1})/(?P<pk>[0-9]+)/add/$',
        tracker_views.TrackerDocumentAddView.as_view(),
        name='tracker_document_add'
    ),
    url(
        r'^document/project/(?P<pk>[0-9]+)/add/$',
        tracker_views.TrackerProjectDocumentAddView.as_view(),
        name='tracker_project_document_add'
    ),
    url(
        r'^document/edit/(?P<pk>\d+)/$',
        tracker_views.TrackerDocumentEditView.as_view(),
        name='tracker_document_edit'
    ),
    url(
        r'^document/project/edit/(?P<pk>\d+)/$',
        tracker_views.TrackerProjectDocumentEditView.as_view(),
        name='tracker_project_document_edit'
    ),
    url(
        r'^document/delete/(?P<pk>\d+)/$',
        tracker_views.TrackerDocumentDeleteView.as_view(),
        name='tracker_document_delete'
    ),
    url(
        r'^document/project/delete/(?P<pk>\d+)/$',
        tracker_views.TrackerProjectDocumentDeleteView.as_view(),
        name='tracker_project_document_delete'
    ),
    url(
        r'^document/download/(?P<pk>\d+)/$',
        tracker_views.TrackerDocumentDownloadView.as_view(),
        name='tracker_document_download'
    ),
    url(
        r'^document/project/download/(?P<pk>\d+)/$',
        tracker_views.TrackerProjectDocumentDownloadView.as_view(),
        name='tracker_project_document_download'
    ),
]

urlpatterns = user_urlpatterns + generic_urlpatterns + tracker_urlpatterns
