# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from rest_framework import generics, status

from web.api.permissions import RoleAccessPermission
from web.api.views import QuerysetMixin, JWTPayloadMixin, WhistleGenericViewMixin
from .. import serializers
from web.drf import exceptions as django_api_exception


class TrackerMessageMixin(
        JWTPayloadMixin):
    """
    Message Mixin
    """
    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            document = profile.get_message(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, document)
            return document
        except ObjectDoesNotExist as err:
            raise django_api_exception.MessageAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.MessageSerializer
        else:
            self.serializer_class = output_serializer


class TrackerMessageListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all messages
    """
    serializer_class = serializers.MessageSerializer

    def __init__(self, *args, **kwargs):
        self.message_response_include_fields = [
            'id', 'body', 'talk', 'sender', 'date_create', 'media_set'
        ]
        self.talk_response_include_fields = [
            'id', 'code', 'content_type_name', 'object_id'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo'
        ]
        super(TrackerMessageListView, self).__init__( *args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_received_messages()
        return super(TrackerMessageListView, self).get_queryset()


class TrackerMessageAddView(
        WhistleGenericViewMixin,
        TrackerMessageMixin,
        generics.CreateAPIView):
    """
    Add a message
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.MessageAddSerializer

    def __init__(self, *args, **kwargs):
        self.message_request_include_fields = [
            'id', 'body', 'talk'
        ]
        self.talk_request_include_fields = [
            'id', 'content_type', 'object_id'
        ]
        self.message_response_include_fields = [
            'id', 'body', 'talk', 'sender', 'date_create', 'messagefileassignment_set'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'role', 'company'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'category', 'color_project'
        ]
        self.talk_response_include_fields = [
            'id', 'code', 'content_type_name', 'object_id'
        ]
        super(TrackerMessageAddView, self).__init__( *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True
        if not 'talk' in request.data:
            request.data['talk'] = dict()

        request.data['talk']['content_type'] = ContentType.objects.get(model=self.kwargs['type'])
        request.data['talk']['content_type_id'] = request.data['talk']['content_type'].id
        request.data['talk']['object_id'] = self.kwargs['pk']
        return self.create(request, *args, **kwargs)


class TrackerMessageDetailView(
        TrackerMessageMixin,
        generics.RetrieveAPIView):
    """
    Get a message
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.MessageSerializer

    def __init__(self, *args, **kwargs):
        self.message_response_include_fields = [
            'id', 'body', 'talk', 'sender', 'date_create'
        ]
        self.talk_response_include_fields = [
            'id', 'code', 'content_type_name', 'object_id'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo'
        ]
        super(TrackerMessageDetailView, self).__init__( *args, **kwargs)


class TrackerMessageDeleteView(
        TrackerMessageMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a message
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.MessageSerializer

    def __init__(self, *args, **kwargs):
        self.message_response_include_fields = [
            'id', 'body', 'talk', 'sender', 'date_create'
        ]
        self.talk_response_include_fields = [
            'id', 'code'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo'
        ]
        super(TrackerMessageDeleteView, self).__init__( *args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_message(instance)


class TrackerTalkMixin(
        JWTPayloadMixin):
    """
    Talk Mixin
    """
    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            document = profile.get_talk(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, document)
            return document
        except ObjectDoesNotExist as err:
            raise django_api_exception.TalkAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

class TrackerTalkListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all messages
    """
    serializer_class = serializers.TalkMessageSerializer

    def __init__(self, *args, **kwargs):
        self.talk_message_response_include_fields = [
            'id', 'code', 'object_id', 'messages'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo'
        ]
        super(TrackerTalkListView, self).__init__( *args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_all_talks()
        return super(TrackerTalkListView, self).get_queryset()


class TrackerTalkDetailView(
        TrackerTalkMixin,
        generics.RetrieveAPIView):
    """
    Get a talk with all messages
    """
    serializer_class = serializers.TalkMessageSerializer

    def __init__(self, *args, **kwargs):
        self.talk_message_response_include_fields = ['id', 'code', 'messages']
        super(TrackerTalkDetailView, self).__init__( *args, **kwargs)

class TrackerTalkDeleteView(
        TrackerTalkMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a talk
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.TalkMessageSerializer

    def __init__(self, *args, **kwargs):
        self.talk_message_response_include_fields = ['id', 'code', 'messages']
        super(TrackerTalkDeleteView, self).__init__( *args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_talk(instance)
