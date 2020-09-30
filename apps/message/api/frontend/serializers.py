# -*- coding: utf-8 -*-
import os

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers, status
from rest_framework.serializers import ValidationError

from apps.profile.api.frontend.serializers import ProfileSerializer
from apps.profile.models import Profile
from ... import models
from apps.profile import models as profile_models
from apps.project import models as project_models
from apps.profile.api.frontend import serializers as profile_serializers
from web.drf import exceptions as django_api_exception
from web.api.views import JWTPayloadMixin
from web.api.serializers import DynamicFieldsModelSerializer
from ...models import MessageFileAssignment
from ...signals import get_filetype


class MessageFileAssignmentSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = models.MessageFileAssignment
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.messagefileassignment_request_include_fields
        return super(MessageFileAssignmentSerializer, self).get_field_names(*args, **kwargs)

class TalkSerializer(
        DynamicFieldsModelSerializer):
    content_type_name = serializers.ReadOnlyField(source="get_content_type_model")

    class Meta:
        model = models.Talk
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.talk_response_include_fields
        return super(TalkSerializer, self).get_field_names(*args, **kwargs)


class MessageSerializer(
        DynamicFieldsModelSerializer):
    talk = TalkSerializer()
    sender = profile_serializers.ProfileSerializer()
    files = serializers.SerializerMethodField()

    class Meta:
        model = models.Message
        fields = '__all__'

    def get_files(self, obj):
        media_list = []
        request = self.context['request']
        medias = MessageFileAssignment.objects.filter(message=obj)
        for media in medias:
            try:
                photo_url = media.media.url
                protocol = request.is_secure()
                if protocol:
                    protocol = 'https://'
                else:
                    protocol = 'http://'
                host = request.get_host()
                media_url = protocol + host + photo_url
            except:
                media_url = None
            name, extension = os.path.splitext(media.media.name)
            if extension == '.mp3':
                type = 'audio/mp3'
            else:
                type = get_filetype(media.media)
            media_list.append(
                {
                    "media_url": media_url,
                    "size": media.media.size,
                    "name": name.split('/')[-1],
                    "extension": extension,
                    "type": type,
                    "message": media.message.id
                }
            )
        return media_list


class TalkMessageSerializer(
        DynamicFieldsModelSerializer):
    messages = serializers.SerializerMethodField()

    class Meta:
        model = models.Talk
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.talk_message_response_include_fields
        return super(TalkMessageSerializer, self).get_field_names(*args, **kwargs)

    def get_messages(self, obj):
        messages_list_json = []
        messages = obj.messages.all().values('id', 'body', 'sender', 'date_create')
        for message in messages:
            profile = Profile.objects.get(id=message['sender'])
            message['sender'] = {
                'id': profile.id,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'photo': profile.photo if profile.photo != '' else None,
                'role': profile.role,
                'company': profile.company.id,
            }
        return messages


class TalkAddSerializer(
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Talk
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.talk_request_include_fields
        return super(TalkAddSerializer, self).get_field_names(*args, **kwargs)

class MessageAddSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):
    talk = TalkAddSerializer(required=False)
    media_set = serializers.SerializerMethodField()

    class Meta:
        model = models.Message
        fields = '__all__'

    def get_media_set(self, obj):
        media_list = []
        medias = MessageFileAssignment.objects.filter(message=obj)
        for media in medias:
            try:
                photo_url = media.media.url
                protocol = self.context['request'].is_secure()
                if protocol:
                    protocol = 'https://'
                else:
                    protocol = 'http://'
                host = self.context['request'].get_host()
                media_url = protocol + host + photo_url
            except:
                media_url = None
            name, extension = os.path.splitext(media.media.name)
            media_list.append(
                {
                    "media_url": media_url,
                    "size": media.media.size,
                    "name": name.split('/')[-1],
                    "extension": extension,
                    "message": media.message.id,
                }
            )
        return media_list

    def validate(self, data):
        data = self.request.data
        model_name = ContentType.objects.get(id=data['talk']['content_type_id']).model
        if model_name == 'profile':
            generic_model = profile_models.Profile
        elif model_name == 'company':
            generic_model = profile_models.Company
        elif model_name == 'project':
            generic_model = project_models.Project
        else:
            raise ValidationError("Model Not Found")

        if not generic_model.objects.filter(pk=data['talk']['object_id']):
            raise ValidationError("Object Not Found")
        return data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        self.view = self.get_view
        if self.view:
            return self.view.message_request_include_fields
        return super(MessageAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        message = self.profile.create_message(validated_data)
        files = list(self.request.FILES.values())
        for file in files:
            MessageFileAssignment.objects.create(
                message=message,
                media=file
            )
        message.status = 1
        message.save()
        return message
