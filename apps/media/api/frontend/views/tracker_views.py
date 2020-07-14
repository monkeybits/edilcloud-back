# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import generics, status, views

from web.api.permissions import RoleAccessPermission
from web.api.views import JWTPayloadMixin, WhistleGenericViewMixin, DownloadViewMixin
from .. import serializers
from web.drf import exceptions as django_api_exception


class TrackerPhotoMixin(
        JWTPayloadMixin):
    """
    Company Photo Mixin
    """
    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            photo = profile.get_photo(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, photo)
            return photo
        except ObjectDoesNotExist as err:
            raise django_api_exception.PhotoAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.PhotoSerializer
        else:
            self.serializer_class = output_serializer


class TrackerPhotoDetailView(
        TrackerPhotoMixin,
        generics.RetrieveAPIView):
    """
    Get a single photo
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.PhotoSerializer

    def __init__(self, *args, **kwargs):
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo',
            'is_public', 'tags', 'note', 'size'
        ]
        super(TrackerPhotoDetailView, self).__init__(*args, **kwargs)


class TrackerPhotoAddView(
        WhistleGenericViewMixin,
        TrackerPhotoMixin,
        generics.CreateAPIView):
    """
    Add a single photo
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.PhotoAddSerializer

    def __init__(self, *args, **kwargs):
        self.photo_request_include_fields = [
            'title', 'pub_date', 'photo', 'is_public',
            'content_type', 'object_id', 'tags', 'note'
        ]
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo', 'is_public',
            'tags', 'note', 'photo_64', 'extension'
        ]
        super(TrackerPhotoAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True
        request.data['content_type'] = ContentType.objects.get(model=self.kwargs['type']).id
        request.data['object_id'] = self.kwargs['pk']
        return self.create(request, *args, **kwargs)


class TrackerPhotoEditView(
        WhistleGenericViewMixin,
        TrackerPhotoMixin,
        generics.RetrieveUpdateAPIView):
    """
    Edit a company photo
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.PhotoEditSerializer

    def __init__(self, *args, **kwargs):
        self.photo_request_include_fields = [
            'title', 'pub_date', 'photo', 'note', 'tags'
        ]
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo',
            'tags', 'note', 'is_public', 'photo_64', 'extension'
        ]
        super(TrackerPhotoEditView, self).__init__(*args, **kwargs)

    def put(self, request, *args, **kwargs):
        if not 'photo' in request.data or type(request.data['photo']) == str:
            self.photo_request_include_fields.remove('photo')
        return self.update(request, *args, **kwargs)


class TrackerPhotoDeleteView(
        TrackerPhotoMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a company photo
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.PhotoSerializer

    def __init__(self, *args, **kwargs):
        self.photo_response_include_fields = ['id', 'title', 'pub_date', 'photo', 'tags', 'note']
        super(TrackerPhotoDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_photo(instance)


class TrackerPhotoDownloadView(
        TrackerPhotoMixin, DownloadViewMixin,
        views.APIView):
    """
    Download a document
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1,)
    file_field_name = 'photo'


class TrackerVideoMixin(
        JWTPayloadMixin):
    """
    Company Video Mixin
    """
    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            video = profile.get_video(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, video)
            return video
        except ObjectDoesNotExist as err:
            raise django_api_exception.VideoAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.VideoSerializer
        else:
            self.serializer_class = output_serializer


class TrackerVideoDetailView(
        TrackerVideoMixin,
        generics.RetrieveAPIView):
    """
    Get a single video
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.VideoSerializer

    def __init__(self, *args, **kwargs):
        self.video_response_include_fields = [
            'id', 'title', 'pub_date', 'video',
            'tags', 'note', 'is_public', 'size', 'extension'
        ]
        super(TrackerVideoDetailView, self).__init__(*args, **kwargs)


class TrackerVideoAddView(
        WhistleGenericViewMixin,
        TrackerVideoMixin,
        generics.CreateAPIView):
    """
    Add a single video
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.VideoAddSerializer

    def __init__(self, *args, **kwargs):
        self.video_request_include_fields = [
            'title', 'pub_date', 'video', 'is_public',
            'content_type', 'object_id', 'tags', 'note'
        ]
        self.video_response_include_fields = [
            'id', 'title', 'pub_date', 'video',
            'tags', 'note', 'extension', 'is_public'
        ]
        super(TrackerVideoAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True
        request.data['content_type'] = ContentType.objects.get(model=self.kwargs['type']).id
        request.data['object_id'] = self.kwargs['pk']
        return self.create(request, *args, **kwargs)


class TrackerVideoEditView(
        WhistleGenericViewMixin,
        TrackerVideoMixin,
        generics.RetrieveUpdateAPIView):
    """
    Edit a company video
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.VideoEditSerializer

    def __init__(self, *args, **kwargs):
        self.video_request_include_fields = [
            'title', 'pub_date', 'video', 'tags', 'note'
        ]
        self.video_response_include_fields = [
            'id', 'title', 'pub_date', 'video',
            'tags', 'note', 'extension', 'is_public'
        ]
        super(TrackerVideoEditView, self).__init__(*args, **kwargs)

    def put(self, request, *args, **kwargs):
        if not 'video' in request.data or type(request.data['video']) == str:
            self.video_request_include_fields.remove('video')
        return self.update(request, *args, **kwargs)


class TrackerVideoDeleteView(
        TrackerVideoMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a company video
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.VideoSerializer

    def __init__(self, *args, **kwargs):
        self.video_response_include_fields = ['id', 'title', 'pub_date', 'video', 'tags', 'note']
        super(TrackerVideoDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_video(instance)


class TrackerVideoDownloadView(
        TrackerVideoMixin, DownloadViewMixin,
        views.APIView):
    """
    Download a document
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1,)
    file_field_name = 'video'
