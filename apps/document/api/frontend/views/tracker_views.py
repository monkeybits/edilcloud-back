# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import generics, status, views

from web.api.views import JWTPayloadMixin, WhistleGenericViewMixin, DownloadViewMixin
from web.api.permissions import RoleAccessPermission
from web.drf import exceptions as django_api_exception

from .. import serializers


class TrackerDocumentMixin(
        JWTPayloadMixin):
    """
    Company Document Mixin
    """
    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            document = profile.get_document(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, document)
            return document
        except ObjectDoesNotExist as err:
            raise django_api_exception.DocumentAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.DocumentSerializer
        else:
            self.serializer_class = output_serializer


class TrackerDocumentDetailView(
        TrackerDocumentMixin,
        generics.RetrieveAPIView):
    """
    Get a single document
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, )
    serializer_class = serializers.DocumentSerializer

    def __init__(self, *args, **kwargs):
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document',
            'date_create', 'date_last_modify', 'is_public', 'size'
        ]
        super(TrackerDocumentDetailView, self).__init__(*args, **kwargs)


class TrackerDocumentAddView(
        WhistleGenericViewMixin,
        TrackerDocumentMixin,
        generics.CreateAPIView):
    """
    Add a single document
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.DocumentAddSerializer

    def __init__(self, *args, **kwargs):
        self.document_request_include_fields = [
            'title', 'description', 'document',
            'content_type', 'object_id', 'is_public'
        ]
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document',
            'date_create', 'date_last_modify', 'is_public'
        ]
        super(TrackerDocumentAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True
        request.data['content_type'] = ContentType.objects.get(model=self.kwargs['type']).id
        request.data['object_id'] = self.kwargs['pk']
        return self.create(request, *args, **kwargs)


class TrackerProjectDocumentAddView(
        WhistleGenericViewMixin,
        TrackerDocumentMixin,
        generics.CreateAPIView):
    """
    Add a single document
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, )
    serializer_class = serializers.DocumentAddSerializer

    def __init__(self, *args, **kwargs):
        self.document_request_include_fields = [
            'title', 'description', 'document',
            'content_type', 'object_id', 'is_public'
        ]
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document',
            'date_create', 'date_last_modify', 'is_public'
        ]
        super(TrackerProjectDocumentAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True
        request.data['content_type'] = ContentType.objects.get(model='project').id
        request.data['object_id'] = self.kwargs['pk']
        return self.create(request, *args, **kwargs)


class TrackerDocumentEditView(
        WhistleGenericViewMixin,
        TrackerDocumentMixin,
        generics.RetrieveUpdateAPIView):
    """
    Edit a document
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.DocumentEditSerializer

    def __init__(self, *args, **kwargs):
        self.document_request_include_fields = [
            'title', 'description', 'document'
        ]
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document',
            'date_create', 'date_last_modify', 'is_public'
        ]
        super(TrackerDocumentEditView, self).__init__(*args, **kwargs)

    def put(self, request, *args, **kwargs):
        if not 'document' in request.data or type(request.data['document']) == str:
            self.document_request_include_fields.remove('document')
        return self.update(request, *args, **kwargs)


class TrackerProjectDocumentEditView(
        WhistleGenericViewMixin,
        TrackerDocumentMixin,
        generics.RetrieveUpdateAPIView):
    """
    Edit a document
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, )
    serializer_class = serializers.DocumentEditSerializer

    def __init__(self, *args, **kwargs):
        self.document_request_include_fields = [
            'title', 'description', 'document'
        ]
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document',
            'date_create', 'date_last_modify', 'is_public'
        ]
        super(TrackerProjectDocumentEditView, self).__init__(*args, **kwargs)

    def put(self, request, *args, **kwargs):
        if not 'document' in request.data or type(request.data['document']) == str:
            self.document_request_include_fields.remove('document')
        return self.update(request, *args, **kwargs)


class TrackerDocumentDeleteView(
        WhistleGenericViewMixin,
        TrackerDocumentMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a document
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.DocumentSerializer

    def __init__(self, *args, **kwargs):
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document',
            'date_create', 'date_last_modify'
        ]
        super(TrackerDocumentDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_document(instance)


class TrackerProjectDocumentDeleteView(
        WhistleGenericViewMixin,
        TrackerDocumentMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a document
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, )
    serializer_class = serializers.DocumentSerializer

    def __init__(self, *args, **kwargs):
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document',
            'date_create', 'date_last_modify'
        ]
        super(TrackerProjectDocumentDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_document(instance)


class TrackerDocumentDownloadView(
        TrackerDocumentMixin, DownloadViewMixin,
        views.APIView):
    """
    Download a document
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    file_field_name = 'document'


class TrackerProjectDocumentDownloadView(
        TrackerDocumentMixin, DownloadViewMixin,
        views.APIView):
    """
    Download a document
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, settings.LEVEL_2, )
    file_field_name = 'document'