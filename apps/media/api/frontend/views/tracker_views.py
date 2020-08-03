# -*- coding: utf-8 -*-
import os
import pathlib
import shutil

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from rest_framework import generics, status, views
from rest_framework.response import Response

from apps.profile.models import Company
from apps.project.models import Project
from apps.quotation.models import Bom
from web.api.permissions import RoleAccessPermission
from web.api.views import JWTPayloadMixin, WhistleGenericViewMixin, DownloadViewMixin, get_media_root
from .. import serializers
from web.drf import exceptions as django_api_exception
from apps.profile import models as profile_models
from apps.project import models as project_models
from apps.quotation import models as quotation_models

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

def get_upload_folder_path(instance, subpath, folder, is_public, create=False):
    media_dir1 = instance._meta.model_name
    media_dir2 = slugify(instance.__str__().lower())
    if media_dir1 == 'project':
        media_dir1 = 'genericproject'
        media_dir2 = instance.pk
    media_root = get_media_root(is_public)
    if create:
        if subpath == '' or subpath == '/':
            os.makedirs(os.path.join(media_root, 'photo', format(media_dir1), format(media_dir2),  folder))
        else:
            if len(subpath.split('/')) == 3:
                return False
            os.makedirs(os.path.join(media_root, 'photo', format(media_dir1), format(media_dir2), subpath,folder))

    return os.path.join(media_root, 'photo', format(media_dir1), format(media_dir2))

def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return "{:0.2f}{}{}".format(b, unit, suffix)
        b /= factor
    return "{:0.2f}Y{}".format(b, suffix)

class TrackerFolderAdd(generics.CreateAPIView):
    """
    Folder add
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS

    def post(self, request, *args, **kwargs):
        content_type = ContentType.objects.get(model=self.kwargs['type'])
        folder_name = request.data['name']
        subpath = request.data['path']
        model_name = content_type.model
        if model_name == 'company':
            generic_model = profile_models.Company
        elif model_name == 'project':
            generic_model = project_models.Project
        elif model_name == 'bom':
            generic_model = quotation_models.Bom
        else:
            raise ValidationError("Model Not Found")

        if not generic_model.objects.filter(pk=self.kwargs['pk']):
            raise ValidationError("Object Not Found")

        if model_name == 'project':
            gen_mod = Project.objects.get(id=self.kwargs['pk'])
        elif model_name == 'company':
            gen_mod = Company.objects.get(id=self.kwargs['pk'])
        elif model_name == 'bom':
            gen_mod = Bom.objects.get(id=self.kwargs['pk'])
        try:
            company_folder = get_upload_folder_path(gen_mod, subpath, folder_name, False, True)
            if company_folder == False:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={
                    'error': 'Folder not created. Max subfolders limit is 3'
                })
            folders_list = os.walk(company_folder)
            listOfFiles = list()
            if model_name == 'project':
                for (dirpath, dirnames, filenames) in folders_list:
                    listOfFiles += [
                        {
                            'path': os.path.join(dirpath, dirname).split('genericproject/' + self.kwargs['pk'] + '/')[
                                1],
                            'size': get_size_format(os.path.getsize(os.path.join(dirpath, dirname)))
                        }
                        for dirname in dirnames
                    ]
            else:
                for (dirpath, dirnames, filenames) in folders_list:
                    listOfFiles += [
                        {
                            'path':
                                os.path.join(dirpath, dirname).split(slugify(gen_mod.__str__().lower()))[1].split('/', 1)[
                                    1],
                            'size': get_size_format(os.path.getsize(os.path.join(dirpath, dirname)))
                        }
                        for dirname in dirnames
                    ]
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'error': "Folder already exists"
            })
        return Response(status=status.HTTP_201_CREATED, data=listOfFiles)

class TrackerFolderList(generics.CreateAPIView):
    """
    Folder add
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS

    def get(self, request, *args, **kwargs):
        content_type = ContentType.objects.get(model=self.kwargs['type'])
        model_name = content_type.model
        if model_name == 'company':
            generic_model = profile_models.Company
        elif model_name == 'project':
            generic_model = project_models.Project
        elif model_name == 'bom':
            generic_model = quotation_models.Bom
        else:
            raise ValidationError("Model Not Found")

        if not generic_model.objects.filter(pk=self.kwargs['pk']):
            raise ValidationError("Object Not Found")

        if model_name == 'project':
            gen_mod = Project.objects.get(id=self.kwargs['pk'])
        elif model_name == 'company':
            gen_mod = Company.objects.get(id=self.kwargs['pk'])
        elif model_name == 'bom':
            gen_mod = Bom.objects.get(id=self.kwargs['pk'])
        company_folder = get_upload_folder_path(gen_mod, '', '', False)
        if company_folder == False:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'error': 'Folder not created. Max subfolders limit is 3'
            })
        folders_list = os.walk(company_folder)
        print(folders_list)
        listOfFiles = list()
        if model_name == 'project':
            for (dirpath, dirnames, filenames) in folders_list:
                listOfFiles += [
                    {
                        'path': os.path.join(dirpath, dirname).split('genericproject/' + self.kwargs['pk'] + '/')[1],
                        'size': get_size_format(os.path.getsize(os.path.join(dirpath, dirname)))
                    }
                    for dirname in dirnames
                ]
        else:
            for (dirpath, dirnames, filenames) in folders_list:
                listOfFiles += [
                    {
                        'path': os.path.join(dirpath, dirname).split(slugify(gen_mod.__str__().lower()))[1].split('/', 1)[1],
                        'size': get_size_format(os.path.getsize(os.path.join(dirpath, dirname)))
                    }
                    for dirname in dirnames
                ]
        return Response(status=status.HTTP_200_OK, data=listOfFiles)

def get_upload_folder_path2(instance, subpath, folder, is_public, create=False, type='photo'):
    media_dir1 = instance._meta.model_name
    media_dir2 = slugify(instance.__str__().lower())
    if media_dir1 == 'project':
        media_dir1 = 'genericproject'
        media_dir2 = instance.pk
    media_root = get_media_root(is_public)
    if create:
        if subpath == '' or subpath == '/':
            os.makedirs(os.path.join(media_root, type, format(media_dir1), format(media_dir2),  folder))
        else:
            os.makedirs(os.path.join(media_root, type, format(media_dir1), format(media_dir2), subpath,folder))

    return os.path.join(media_root, type, format(media_dir1), format(media_dir2))

class TrackerFolderDeleteView(generics.DestroyAPIView):
    """
    Delete a company photo
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)

    def delete(self, request, *args, **kwargs):
        folder_name = self.request.query_params.get('name')
        if folder_name:
            content_type = ContentType.objects.get(model=self.kwargs['type'])
            model_name = content_type.model
            if model_name == 'company':
                generic_model = profile_models.Company
            elif model_name == 'project':
                generic_model = project_models.Project
            elif model_name == 'bom':
                generic_model = quotation_models.Bom
            else:
                raise ValidationError("Model Not Found")

            if not generic_model.objects.filter(pk=self.kwargs['pk']):
                raise ValidationError("Object Not Found")

            if model_name == 'project':
                gen_mod = Project.objects.get(id=self.kwargs['pk'])
            elif model_name == 'company':
                gen_mod = Company.objects.get(id=self.kwargs['pk'])
            elif model_name == 'bom':
                gen_mod = Bom.objects.get(id=self.kwargs['pk'])
            for type in ['photo', 'video', 'document']:
                company_folder = get_upload_folder_path2(gen_mod, '', '', False, False, type)
                if company_folder == False:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={
                        'error': 'Folder not created. Max subfolders limit is 3'
                    })
                try:
                    shutil.rmtree(os.path.join(company_folder, folder_name))  # remove dir and all contains
                except Exception as e:
                    continue
            return Response(status=status.HTTP_200_OK, data="Folder deleted successfully")
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Enter a folder name for deleting one")

