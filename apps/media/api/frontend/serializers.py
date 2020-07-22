# -*- coding: utf-8 -*-

import base64
from django.utils.translation import ugettext_lazy as _
from django.core.files import File
from rest_framework import serializers, status
from rest_framework.serializers import ValidationError

from ... import models
from apps.profile import models as profile_models
from apps.project import models as project_models
from apps.quotation import models as quotation_models
from web.drf import exceptions as django_api_exception
from web.api.views import JWTPayloadMixin, ArrayFieldInMultipartMixin
from web.api.serializers import DynamicFieldsModelSerializer


class PhotoSerializer(
        DynamicFieldsModelSerializer):

    extension = serializers.SerializerMethodField()
    photo_64 = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    relative_path = serializers.SerializerMethodField()
    folder_relative_path = serializers.SerializerMethodField()

    class Meta:
        model = models.Photo
        fields = '__all__'

    def get_extension(self, obj):
        return obj.get_file_extension()[1:]

    def get_relative_path(self, obj):
        url = obj.photo.url
        if '%20' in obj.photo.url:
            url = obj.photo.url.replace('%20', ' ')
        if len(url.split(obj.content_object.slug.lower())) >= 2:
            return url.split(obj.content_object.slug.lower())[1]
        else:
            return url

    def get_folder_relative_path(self, obj):
        url = obj.photo.url
        if '%20' in obj.photo.url:
            url = obj.photo.url.replace('%20', ' ')
        if len(url.split(obj.content_object.slug.lower())) >= 2:
            splitted = url.split(obj.content_object.slug.lower())[1].rsplit('/', 1)[0]
            print(splitted)
            if splitted != '' and splitted != '/':
                return splitted.split('/', 1)[1]
            return splitted
        else:
            return url

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.photo_response_include_fields
        return super(PhotoSerializer, self).get_field_names(*args, **kwargs)

    def get_photo_64(self, obj):
        f = open(obj.photo.path, 'rb')
        image = File(f)
        data = base64.b64encode(image.read())
        f.close()
        return data

    def get_size(self, obj):
        return obj.photo.size


class PhotoAddSerializer(
        JWTPayloadMixin,
        ArrayFieldInMultipartMixin,
        DynamicFieldsModelSerializer):

    photo_64 = serializers.SerializerMethodField(read_only=True)
    extension = serializers.SerializerMethodField(read_only=True)
    size = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Photo
        fields = '__all__'

    def validate(self, data):
        model_name = data['content_type'].model
        if model_name == 'company':
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
            return self.view.photo_request_include_fields
        return super(PhotoAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        self.get_array_from_string(validated_data)
        if 'additional_path' in self.request.data:
            validated_data['additional_path'] = self.request.data['additional_path']
        try:
            photo = self.profile.create_photo(validated_data)
            return photo
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def get_photo_64(self, obj):
        f = open(obj.photo.path, 'rb')
        image = File(f)
        data = base64.b64encode(image.read())
        f.close()
        return data

    def get_size(self, obj):
        return obj.photo.size

    def get_extension(self, obj):
        return obj.get_file_extension()[1:]


class PhotoEditSerializer(
        JWTPayloadMixin,
        ArrayFieldInMultipartMixin,
        DynamicFieldsModelSerializer):

    photo_64 = serializers.SerializerMethodField(read_only=True)
    extension = serializers.SerializerMethodField(read_only=True)
    size = serializers.SerializerMethodField()

    class Meta:
        model = models.Photo
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
            return self.view.photo_request_include_fields
        return super(PhotoEditSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        self.get_array_from_string(validated_data)
        validated_data['id'] = instance.id
        video = self.profile.edit_photo(validated_data)
        return video

    def get_photo_64(self, obj):
        f = open(obj.photo.path, 'rb')
        image = File(f)
        data = base64.b64encode(image.read())
        f.close()
        return data

    def get_size(self, obj):
        return obj.photo.size

    def get_extension(self, obj):
        return obj.get_file_extension()[1:]


class VideoSerializer(
        DynamicFieldsModelSerializer):

    extension = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    relative_path = serializers.SerializerMethodField()
    folder_relative_path = serializers.SerializerMethodField()

    class Meta:
        model = models.Video
        fields = '__all__'

    def get_size(self, obj):
        return obj.video.size

    def get_extension(self, obj):
        return obj.get_file_extension()

    def get_relative_path(self, obj):
        url = obj.video.url
        if '%20' in obj.video.url:
            url = obj.video.url.replace('%20', ' ')
        if len(url.split(obj.content_object.slug.lower())) >= 2:
            return url.split(obj.content_object.slug.lower())[1]
        else:
            return url

    def get_folder_relative_path(self, obj):
        url = obj.video.url
        if '%20' in obj.video.url:
            url = obj.video.url.replace('%20', ' ')
        if len(url.split(obj.content_object.slug.lower())) >= 2:
            splitted = url.split(obj.content_object.slug.lower())[1].rsplit('/', 1)[0]
            if splitted != '':
                return splitted.split('/', 1)[1]
            return splitted
        else:
            return url

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.video_response_include_fields
        return super(VideoSerializer, self).get_field_names(*args, **kwargs)


class VideoAddSerializer(
        JWTPayloadMixin,
        ArrayFieldInMultipartMixin,
        DynamicFieldsModelSerializer):

    extension = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Video
        fields = '__all__'

    def validate(self, data):
        model_name = data['content_type'].model
        if model_name == 'company':
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
            return self.view.video_request_include_fields
        return super(VideoAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        self.get_array_from_string(validated_data)
        try:
            if 'additional_path' in self.request.data:
                validated_data['additional_path'] = self.request.data['additional_path']
            video = self.profile.create_video(validated_data)
            return video
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def get_extension(self, obj):
        return obj.get_file_extension()


class VideoEditSerializer(
        JWTPayloadMixin,
        ArrayFieldInMultipartMixin,
        DynamicFieldsModelSerializer):

    extension = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Video
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
            return self.view.video_request_include_fields
        return super(VideoEditSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        self.get_array_from_string(validated_data)
        validated_data['id'] = instance.id
        video = self.profile.edit_video(validated_data)
        return video

    def get_extension(self, obj):
        return obj.get_file_extension()