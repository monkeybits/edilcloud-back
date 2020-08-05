# -*- coding: utf-8 -*-

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

    class Meta:
        model = models.Message
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.message_response_include_fields
        return super(MessageSerializer, self).get_field_names(*args, **kwargs)


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
        JWTPayloadMixin,
        DynamicFieldsModelSerializer):
    talk = TalkAddSerializer(required=False)

    class Meta:
        model = models.Message
        fields = '__all__'

    def validate(self, data):
        data = self.request.data
        model_name = data['talk']['content_type'].model
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
        try:
            message = self.profile.create_message(validated_data)
            return message
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )
