# -*- coding: utf-8 -*-
import json

from rest_framework import serializers

from apps.profile.api.frontend import serializers as profile_serializers
from apps.project.models import Task, Project, Activity, Post, Comment
from web.api.serializers import DynamicFieldsModelSerializer
from web.api.views import JWTPayloadMixin
from ... import models


class NotifySerializer(
        DynamicFieldsModelSerializer):
    sender = profile_serializers.ProfileSerializer()
    body = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField(source='get_content_type')
    project_id = serializers.SerializerMethodField()

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


    def get_project_id(self, obj):
        if obj.content_type.name == 'project':
            project = Project.objects.get(id=obj.object_id)
            return project.id
        elif obj.content_type.name == 'task':
            task = Task.objects.get(id=obj.object_id)
            return task.project.id
        elif obj.content_type.name == 'activity':
            activity = Activity.objects.get(id=obj.object_id)
            return activity.task.project.id
        elif obj.content_type.name == 'post':
            post = Post.objects.get(id=obj.object_id)
            if post.task is not None:
                return post.task.project.id
            else:
                return post.sub_task.task.project.id
        elif obj.content_type.name == 'comment':
            comment = Comment.objects.get(id=obj.object_id)
            if comment.post.task is not None:
                return comment.post.task.project.id
            else:
                return comment.post.sub_task.task.project.id
        else:
            return None


    def get_body(self, obj):
        try:
            return json.loads(obj.body)
        except:
            return {}

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

class NotificationRecipientReadAllSerializer(
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
        return super(NotificationRecipientReadAllSerializer, self).get_field_names(*args, **kwargs)

    def post(self, validated_data):
        notification_recipients = self.profile.list_notification_receipient_new()
        for instance in notification_recipients:
            notification_recipient = self.profile.edit_notification_receipient(instance)
        return {}
