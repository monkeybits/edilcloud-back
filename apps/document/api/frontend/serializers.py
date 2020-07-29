# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers, status
from rest_framework.serializers import ValidationError

from ... import models
from apps.profile import models as profile_models
from apps.project import models as project_models
from apps.quotation import models as quotation_models
from web.drf import exceptions as django_api_exception
from web.api.views import JWTPayloadMixin
from web.api.serializers import DynamicFieldsModelSerializer


class DocumentSerializer(
        DynamicFieldsModelSerializer):
    extension = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField(read_only=True)
    relative_path = serializers.SerializerMethodField()
    folder_relative_path = serializers.SerializerMethodField()

    class Meta:
        model = models.Document
        fields = '__all__'

    def get_size(self, obj):
        return obj.document.size

    def get_extension(self, obj):
        return obj.get_file_extension()[1:]

    def get_folder_relative_path(self, obj):
        url = obj.document.url
        if '%20' in obj.document.url:
            url = obj.document.url.replace('%20', ' ')
        if hasattr(obj.content_object, 'slug'):
            identity_folder = obj.content_object.slug
        else:
            identity_folder = str(obj.content_object.id)
        if len(url.split(identity_folder)) >= 2:
            splitted = url.split(identity_folder)[1].rsplit('/', 1)[0]
            if splitted != '':
                return splitted.split('/', 1)[1]
            return splitted
        else:
            return url

    def get_relative_path(self, obj):
        url = obj.document.url
        if '%20' in obj.document.url:
            url = obj.document.url.replace('%20', ' ')
        if hasattr(obj.content_object, 'slug'):
            identity_folder = obj.content_object.slug
        else:
            identity_folder = str(obj.content_object.id)
        if len(url.split(identity_folder)) >= 2:
            return url.split(identity_folder)[1]
        else:
            return url

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.document_response_include_fields
        return super(DocumentSerializer, self).get_field_names(*args, **kwargs)


class DocumentAddSerializer(
        JWTPayloadMixin,
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Document
        fields = '__all__'

    def validate(self, data):
        model_name = data['content_type'].model
        if model_name == 'profile':
            generic_model = profile_models.Profile
        elif model_name == 'company':
            generic_model = profile_models.Company
        elif model_name == 'project':
            generic_model = project_models.Project
        elif model_name == 'bom':
            generic_model = quotation_models.Bom
        else:
            raise ValidationError("Model Not Found")

        if not generic_model.objects.filter(pk=data['object_id']):
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
            return self.view.document_request_include_fields
        return super(DocumentAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        try:
            if 'additional_path' in self.request.data:
                validated_data['additional_path'] = self.request.data['additional_path']
            document = self.profile.create_document(validated_data)
            return document
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class DocumentEditSerializer(
        JWTPayloadMixin,
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Document
        fields = '__all__'

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
            return self.view.document_request_include_fields
        return super(DocumentEditSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        validated_data['id'] = instance.id
        document = self.profile.edit_document(validated_data)
        return document
