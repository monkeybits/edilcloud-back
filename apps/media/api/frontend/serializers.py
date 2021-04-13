# -*- coding: utf-8 -*-

import base64
import os

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.core.files import File
from rest_framework import serializers, status
from rest_framework.serializers import ValidationError

from apps.profile.models import Company
from apps.project.models import Project
from apps.quotation.models import Bom
from web.utils import check_limitation_plan, get_media_size
from ... import models
from apps.profile import models as profile_models
from apps.project import models as project_models
from apps.quotation import models as quotation_models
from web.drf import exceptions as django_api_exception
from web.api.views import JWTPayloadMixin, ArrayFieldInMultipartMixin, get_media_root
from web.api.serializers import DynamicFieldsModelSerializer
from django.utils.text import slugify
from apps.document.api.frontend.serializers import DocumentSerializer


class PhotoSerializer(
    DynamicFieldsModelSerializer):
    extension = serializers.SerializerMethodField()
    photo_64 = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
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
        if hasattr(obj.content_object, 'slug'):
            identity_folder = obj.content_object.slug
        else:
            identity_folder = str(obj.content_object.id)
        if len(url.split(identity_folder)) >= 2:
            return url.split(identity_folder)[1]
        else:
            return url

    def get_folder_relative_path(self, obj):
        url = obj.photo.url
        if '%20' in obj.photo.url:
            url = obj.photo.url.replace('%20', ' ')
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

    def get_photo(self, obj):
        try:
            photo_url = obj.photo.url
            protocol = self.context['request'].is_secure()
            if protocol:
                protocol = 'https://'
            else:
                protocol = 'http://'
            host = self.context['request'].get_host()
            media_url = protocol + host + photo_url
        except:
            media_url = None

        return media_url

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
            check_limitation_plan(self.profile.company.customer, 'size',
                                  get_media_size(self.profile, validated_data)['total_size'])
            photo = self.profile.create_photo(validated_data)
            return photo
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request,
                _("{}".format(err.msg if hasattr(err, 'msg') else err))
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


def get_upload_folder_path2(instance, subpath, folder, is_public, create=False, type='photo'):
    media_dir1 = instance._meta.model_name
    media_dir2 = slugify(instance.__str__().lower())
    if media_dir1 == 'project':
        media_dir1 = 'genericproject'
        media_dir2 = instance.pk
    media_root = get_media_root(is_public)
    if create:
        if subpath == '' or subpath == '/':
            os.makedirs(os.path.join(media_root, type, format(media_dir1), format(media_dir2), folder))
        else:
            os.makedirs(os.path.join(media_root, type, format(media_dir1), format(media_dir2), subpath, folder))

    return os.path.join(media_root, type, format(media_dir1), format(media_dir2))


class PhotoMoveSerializer(
    JWTPayloadMixin,
    ArrayFieldInMultipartMixin,
    DynamicFieldsModelSerializer):
    to = serializers.SerializerMethodField()

    class Meta:
        model = models.Photo
        fields = '__all__'

    # def validate(self, data):
    #     model_name = data['content_type'].model
    #     if model_name == 'company':
    #         generic_model = profile_models.Company
    #     elif model_name == 'project':
    #         generic_model = project_models.Project
    #     elif model_name == 'bom':
    #         generic_model = quotation_models.Bom
    #     else:
    #         raise ValidationError("Model Not Found")
    #
    #     if not generic_model.objects.filter(pk=data['object_id']):
    #         raise ValidationError("Object Not Found")
    #     return data

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
        return super(PhotoMoveSerializer, self).get_field_names(*args, **kwargs)

    def get_to(self, obj):
        return self.request.data['to']

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
        if hasattr(obj.content_object, 'slug'):
            identity_folder = obj.content_object.slug
        else:
            identity_folder = str(obj.content_object.id)
        if len(url.split(identity_folder)) >= 2:
            return url.split(identity_folder)[1]
        else:
            return url

    def get_folder_relative_path(self, obj):
        url = obj.video.url
        if '%20' in obj.video.url:
            url = obj.video.url.replace('%20', ' ')
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
        check_limitation_plan(self.profile.company.customer, 'size',
                              get_media_size(self.profile, validated_data)['total_size'])
        self.get_array_from_string(validated_data)
        try:
            if 'additional_path' in self.request.data:
                validated_data['additional_path'] = self.request.data['additional_path']
            video = self.profile.create_video(validated_data)
            return video
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request,
                _("{}".format(err.msg if hasattr(err, 'msg') else err))
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


class FolderSerializer(
    JWTPayloadMixin,
    DynamicFieldsModelSerializer):
    folders = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()

    class Meta:
        model = models.Folder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    full_path = ""

    def get_folder_path(self, obj):
        global full_path
        if obj.parent:
            root_folder = obj.parent
            path = self.get_folder_path(root_folder)
            full_path += "/{}".format(path)
        else:
            path = obj.name
        return path

    def get_folders(self, obj):
        global full_path
        full_path = ""
        self.get_folder_path(obj)
        data = FolderSerializer(obj.folders.all(), many=True, context=self.context).data
        return data

    def get_path(self, obj):
        global full_path
        full_path = ""
        self.get_folder_path(obj)
        return (full_path + '/{}'.format(obj.name)).split('/', 1)[1]

    def get_media(self, obj):
        photos = PhotoSerializer(obj.photo_set.all(), many=True, context=self.context)
        videos = VideoSerializer(obj.video_set.all(), many=True, context=self.context)
        documents = DocumentSerializer(obj.document_set.all(), many=True, context=self.context)
        return {
            'photo': photos.data,
            'video': videos.data,
            'document': documents.data
        }


class FolderStructureSerializer(
    DynamicFieldsModelSerializer):
    class Meta:
        model = models.Folder
        fields = '__all__'


class FolderAddSerializer(
    JWTPayloadMixin,
    ArrayFieldInMultipartMixin,
    DynamicFieldsModelSerializer):
    folders = serializers.SerializerMethodField()

    class Meta:
        model = models.Folder
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

    def get_folders(self, obj):
        return FolderSerializer(obj.folders.all(), many=True).data

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
            return self.view.folder_request_include_fields
        return super(FolderAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        check_limitation_plan(self.profile.company.customer, 'size',
                              get_media_size(self.profile, validated_data)['total_size'])
        self.get_array_from_string(validated_data)
        folder = self.profile.create_folder(validated_data)
        if folder == 400:
            raise serializers.ValidationError("Folder not created. Max subfolders limit is 3")

        return folder


class FolderEditSerializer(
    JWTPayloadMixin,
    ArrayFieldInMultipartMixin,
    DynamicFieldsModelSerializer):
    folders = serializers.SerializerMethodField()

    class Meta:
        model = models.Folder
        fields = '__all__'

    def get_folders(self, obj):
        return FolderSerializer(obj.folders.all(), many=True).data

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
            return self.view.folder_request_include_fields
        return super(FolderEditSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        self.get_array_from_string(validated_data)
        validated_data['id'] = instance.id
        video = self.profile.edit_folder(validated_data)
        return video
