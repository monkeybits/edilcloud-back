# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from rest_framework import generics, status
from rest_framework.response import Response

from web.api.views import JWTPayloadMixin, WhistleGenericViewMixin
from web.api.permissions import RoleAccessPermission
from web.api.views import QuerysetMixin
from web.drf import exceptions as django_api_exception
from .. import serializers
from .... import models


class TrackerNotificationMixin(
        JWTPayloadMixin):
    """
    Company Project Mixin
    """
    def get_profile(self):
        payload = self.get_payload()
        return self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_object(self):
        try:
            profile = self.get_profile()
            project = profile.get_notification_receipient(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, project)
            return project
        except ObjectDoesNotExist as err:
            raise django_api_exception.NotificationAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.NotificationRecipientSerializer
        else:
            self.serializer_class = output_serializer


class TrackerNotificationRecipientCountDetailView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.RetrieveAPIView):
    """
    Get all notifies w.r.t receiever company profile
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS

    def get(self, request, *args, **kwargs):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        count = profile.list_notification_receipient_count()
        return Response(count)


class TrackerNotificationRecipientListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all notifies w.r.t receiever company profile
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.NotificationRecipientSerializer

    def __init__(self, *args, **kwargs):
        self.notification_recipient_response_include_fields = [
            'id', 'recipient', 'notification', 'is_email',
            'is_notify', 'reading_date', 'date_create', 'status'
        ]
        self.notification_response_include_fields = [
            'id', 'sender', 'subject', 'body', 'content_type',
            'object_id', 'project_id'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'company', 'position'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'category', 'color_project'
        ]
        super(TrackerNotificationRecipientListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        generic = 'list_notification_receipient_' + self.kwargs.get('type')
        self.queryset = getattr(profile, generic)()
        return super(TrackerNotificationRecipientListView, self).get_queryset()


class TrackerNotificationRecipientEventListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all notifies w.r.t receiever company profile
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.NotificationRecipientSerializer

    def __init__(self, *args, **kwargs):
        self.notification_recipient_response_include_fields = [
            'id', 'recipient', 'notification', 'is_email',
            'is_notify', 'reading_date', 'date_create', 'status'
        ]
        self.notification_response_include_fields = [
            'id', 'sender', 'subject', 'body', 'content_type',
            'object_id'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo'
        ]
        super(TrackerNotificationRecipientEventListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_notification_receipient_event(self.kwargs.get('type'))
        return super(TrackerNotificationRecipientEventListView, self).get_queryset()


class TrackerNotificationRecipientReadView(
        WhistleGenericViewMixin,
        TrackerNotificationMixin,
        generics.RetrieveUpdateAPIView):
    """
    Read a single notify
    """
    queryset = models.NotificationRecipient.objects.all()
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.NotificationRecipientReadSerializer

    def __init__(self, *args, **kwargs):
        self.notification_recipient_request_include_fields = []
        self.notification_recipient_response_include_fields = [
            'id', 'recipient', 'notification', 'is_email',
            'is_notify', 'reading_date', 'date_create'
        ]
        self.notification_response_include_fields = [
            'id', 'sender', 'subject', 'body', 'content_type',
            'object_id'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo'
        ]
        super(TrackerNotificationRecipientReadView, self).__init__(*args, **kwargs)

class TrackerNotificationRecipientReadAllView(
        WhistleGenericViewMixin,
        JWTPayloadMixin,
        generics.CreateAPIView):
    """
    Read a single notify
    """
    queryset = models.NotificationRecipient.objects.all()
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.NotificationRecipientReadAllSerializer

    def __init__(self, *args, **kwargs):
        self.notification_recipient_request_include_fields = []
        self.notification_recipient_response_include_fields = [
        ]
        self.notification_response_include_fields = [
        ]
        self.profile_response_include_fields = [
        ]
        super(TrackerNotificationRecipientReadAllView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        generic = 'list_notification_receipient_new'
        self.queryset = getattr(self.profile, generic)()
        return super(TrackerNotificationRecipientReadAllView, self).get_queryset()

    def create(self, request, *args, **kwargs):
        notification_recipients = self.get_queryset()
        for instance in notification_recipients:
            notification_recipient = self.profile.edit_notification_receipient(instance)
        return Response("ok", status.HTTP_200_OK)

class TrackerNotificationDeleteView(
        JWTPayloadMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a company project
    """
    queryset = models.NotificationRecipient.objects.all()
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.NotificationRecipientSerializer

    def __init__(self, *args, **kwargs):
        self.notification_recipient_response_include_fields = [
            'id', 'recipient', 'notification', 'is_email',
            'is_notify', 'reading_date', 'date_create'
        ]
        self.notification_response_include_fields = [
            'id', 'sender', 'subject', 'body', 'content_type',
            'object_id'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo'
        ]
        super(TrackerNotificationDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_notification_receipient(instance)
