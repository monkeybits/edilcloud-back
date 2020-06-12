# -*- coding: utf-8 -*-

from rest_framework import serializers

from apps.profile.api.frontend import serializers as profile_serializers
from web.api.serializers import DynamicFieldsModelSerializer
from web.api.views import JWTPayloadMixin
from ... import models


class NotifySerializer(
        DynamicFieldsModelSerializer):
    sender = profile_serializers.ProfileSerializer()
    content_type = serializers.SerializerMethodField(source='get_content_type')

    class Meta:
        model = models.Notify
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.notification_response_include_fields
        return super(NotifySerializer, self).get_field_names(*args, **kwargs)

    def get_content_type(self, obj):
        return obj.content_type.name


class NotificationRecipientSerializer(
        DynamicFieldsModelSerializer):
    notification = NotifySerializer()
    recipient = profile_serializers.ProfileSerializer()

    class Meta:
        model = models.NotificationRecipient
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.notification_recipient_response_include_fields
        return super(NotificationRecipientSerializer, self).get_field_names(*args, **kwargs)


class NotificationRecipientReadSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin):
    class Meta:
        model = models.NotificationRecipient
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            request = kwargs['context']['request']
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.notification_recipient_request_include_fields
        return super(NotificationRecipientReadSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        notification_recipient = self.profile.edit_notification_receipient(instance)
        return notification_recipient
