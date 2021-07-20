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
from django.core.files.images import ImageFile

from apps.document.models import Document
from apps.media.models import Photo, Video
from apps.profile.models import Company
from apps.project.models import Project
from apps.quotation.models import Bom
from web.api.permissions import RoleAccessPermission
from web.api.views import JWTPayloadMixin, WhistleGenericViewMixin, DownloadViewMixin, get_media_root, QuerysetMixin
from .. import serializers
from web.drf import exceptions as django_api_exception
from apps.profile import models as profile_models
from apps.project import models as project_models
from apps.quotation import models as quotation_models
from ..serializers import FolderSerializer, FolderStructureSerializer


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
            'is_public', 'tags', 'note', 'size', 'folder'
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
            'content_type', 'object_id', 'tags', 'note', 'folder'
        ]
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo', 'is_public',
            'tags', 'note', 'photo_64', 'extension', 'folder'
        ]
        super(TrackerPhotoAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True
        request.data['content_type'] = ContentType.objects.get(model=self.kwargs['type']).id
        request.data['object_id'] = self.kwargs['pk']
        return self.create(request, *args, **kwargs)


class TrackerPhotoMoveView(
    WhistleGenericViewMixin,
    TrackerPhotoMixin,
    generics.UpdateAPIView):
    """
    Move a single photo
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.PhotoMoveSerializer

    def __init__(self, *args, **kwargs):
        self.photo_request_include_fields = [
            'to', 'photo', 'folder'
        ]
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo', 'is_public',
            'tags', 'note', 'photo_64', 'extension', 'folder'
        ]
        super(TrackerPhotoMoveView, self).__init__(*args, **kwargs)

    def put(self, request, *args, **kwargs):
        obj = Photo.objects.get(pk=self.kwargs.get('pk'))
        current_path = obj.photo.url
        from_folder = self.request.data['from']
        to_folder = self.request.data['to']
        if from_folder == '':
            rel_path = current_path.split(current_path.split('/', 6)[-1])
        else:
            rel_path = current_path.split(from_folder)
        if to_folder == '':
            final_path = rel_path[0] + to_folder + rel_path[1].split('/', 1)[1]
        else:
            if from_folder == '':
                final_path = rel_path[0] + to_folder + '/' + current_path.split('/', 6)[-1]
            else:
                final_path = rel_path[0] + to_folder + rel_path[1]
        os.rename(current_path.split('/', 1)[1], final_path.split('/', 1)[1])
        obj.photo.name = final_path.split('/', 1)[1]
        obj.save()
        return Response(status=status.HTTP_200_OK, data="File moved successfully")


class TrackerVideoMoveView(
    WhistleGenericViewMixin,
    TrackerPhotoMixin,
    generics.UpdateAPIView):
    """
    Move a single video
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.PhotoMoveSerializer

    def __init__(self, *args, **kwargs):
        self.photo_request_include_fields = [
            'to', 'folder'
        ]
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo', 'is_public',
            'tags', 'note', 'photo_64', 'extension', 'folder'
        ]
        super(TrackerVideoMoveView, self).__init__(*args, **kwargs)

    def put(self, request, *args, **kwargs):
        obj = Video.objects.get(pk=self.kwargs.get('pk'))
        current_path = obj.video.url
        from_folder = self.request.data['from']
        to_folder = self.request.data['to']
        if from_folder == '':
            rel_path = current_path.split(current_path.split('/', 6)[-1])
        else:
            rel_path = current_path.split(from_folder)
        if to_folder == '':
            final_path = rel_path[0] + to_folder + rel_path[1].split('/', 1)[1]
        else:
            if from_folder == '':
                final_path = rel_path[0] + to_folder + '/' + current_path.split('/', 6)[-1]
            else:
                final_path = rel_path[0] + to_folder + rel_path[1]
        os.rename(current_path.split('/', 1)[1], final_path.split('/', 1)[1])
        obj.video.name = final_path.split('/', 1)[1]
        obj.save()
        return Response(status=status.HTTP_200_OK, data="File moved successfully")


class TrackerDocumentMoveView(
    WhistleGenericViewMixin,
    TrackerPhotoMixin,
    generics.UpdateAPIView):
    """
    Move a single video
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.PhotoMoveSerializer

    def __init__(self, *args, **kwargs):
        self.photo_request_include_fields = [
            'to', 'folder'
        ]
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo', 'is_public',
            'tags', 'note', 'photo_64', 'extension', 'folder'
        ]
        super(TrackerDocumentMoveView, self).__init__(*args, **kwargs)

    def put(self, request, *args, **kwargs):
        obj = Document.objects.get(pk=self.kwargs.get('pk'))
        current_path = obj.document.url
        from_folder = self.request.data['from']
        to_folder = self.request.data['to']
        if from_folder == '':
            rel_path = current_path.split(current_path.split('/', 6)[-1])
        else:
            rel_path = current_path.split(from_folder)
        if to_folder == '':
            final_path = rel_path[0] + to_folder + rel_path[1].split('/', 1)[1]
        else:
            if from_folder == '':
                final_path = rel_path[0] + to_folder + '/' + current_path.split('/', 6)[-1]
            else:
                final_path = rel_path[0] + to_folder + rel_path[1]
        os.rename(current_path.split('/', 1)[1], final_path.split('/', 1)[1])
        obj.document.name = final_path.split('/', 1)[1]
        obj.save()
        return Response(status=status.HTTP_200_OK, data="File moved successfully")


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
            'title', 'pub_date', 'photo', 'note', 'tags', 'folder'
        ]
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo', 'extension',
            'tags', 'note', 'is_public', 'photo_64', 'extension', 'folder'
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
        self.photo_response_include_fields = ['id', 'title', 'pub_date', 'photo', 'tags', 'note', 'folder']
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
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, settings.LEVEL_2)
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


class TrackerFolderMixin(
    JWTPayloadMixin):
    """
    Company Folder Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            folder = profile.get_folder(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, folder)
            return folder
        except ObjectDoesNotExist as err:
            raise django_api_exception.FolderAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.FolderSerializer
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
            'tags', 'note', 'is_public', 'size', 'extension', 'folder'
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
            'content_type', 'object_id', 'tags', 'note', 'folder'
        ]
        self.video_response_include_fields = [
            'id', 'title', 'pub_date', 'video',
            'tags', 'note', 'extension', 'is_public', 'folder'
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
            'title', 'pub_date', 'video', 'tags', 'note', 'folder'
        ]
        self.video_response_include_fields = [
            'id', 'title', 'pub_date', 'video', 'extension',
            'tags', 'note', 'extension', 'is_public', 'folder'
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
        self.video_response_include_fields = ['id', 'title', 'pub_date', 'video', 'tags', 'note', 'folder']
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
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, settings.LEVEL_2)
    file_field_name = 'video'


def get_upload_folder_path(instance, subpath, folder, is_public, create=False):
    media_dir1 = instance._meta.model_name
    media_dir2 = slugify(instance.__str__().lower())
    if media_dir1 == 'project':
        media_dir1 = 'project'
        media_dir2 = instance.pk
    media_root = get_media_root(is_public)
    for name in ['photo', 'video', 'document']:
        if create:
            if subpath == '' or subpath == '/':
                os.makedirs(os.path.join(media_root, name, format(media_dir1), format(media_dir2), folder))
            else:
                if len(subpath.split('/')) == 3:
                    return False
                os.makedirs(os.path.join(media_root, name, format(media_dir1), format(media_dir2), subpath, folder))

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
                            'path': os.path.join(dirpath, dirname).split('project/' + self.kwargs['pk'] + '/')[
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
                                os.path.join(dirpath, dirname).split(slugify(gen_mod.__str__().lower()))[1].split('/',
                                                                                                                  1)[
                                    1],
                            'size': get_size_format(os.path.getsize(os.path.join(dirpath, dirname)))
                        }
                        for dirname in dirnames
                    ]
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'error': e.__str__()
            })
        return Response(status=status.HTTP_201_CREATED, data=listOfFiles)


def get_move_folder_path(instance, source_folder, dest_folder, is_public, create=False):
    media_dir1 = instance._meta.model_name
    media_dir2 = slugify(instance.__str__().lower())
    if media_dir1 == 'project':
        media_dir1 = 'project'
        media_dir2 = instance.pk
    media_root = get_media_root(is_public)
    for name in ['photo', 'video', 'document']:
        source = os.path.join(media_root, name, format(media_dir1), format(media_dir2), source_folder)
        destination = os.path.join(media_root, name, format(media_dir1), format(media_dir2), dest_folder)
        try:
            shutil.move(source, destination)
        except Exception:
            continue
    return os.path.join(media_root, 'photo', format(media_dir1), format(media_dir2))


class TrackerFolderMove(generics.CreateAPIView):
    """
    Folder move
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS

    def post(self, request, *args, **kwargs):
        content_type = ContentType.objects.get(model=self.kwargs['type'])
        from_folder = request.data['from']
        to_folder = request.data['to']
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
            company_folder = get_move_folder_path(gen_mod, from_folder, to_folder, False, True)
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
                            'path': os.path.join(dirpath, dirname).split('project/' + self.kwargs['pk'] + '/')[
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
                                os.path.join(dirpath, dirname).split(slugify(gen_mod.__str__().lower()))[1].split('/',
                                                                                                                  1)[
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


class TrackerFolderList(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all company folders
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = FolderSerializer

    def __init__(self, *args, **kwargs):
        self.folder_response_include_fields = [
            'id', 'title', 'folder', 'is_root', 'note', 'is_public', 'size', 'media'
        ]
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo', 'extension',
            'is_public', 'tags', 'note', 'size', 'folder', 'size'
        ]
        self.video_response_include_fields = [
            'id', 'title', 'pub_date', 'video',
            'tags', 'note', 'extension', 'is_public', 'folder', 'size'
        ]
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document', 'extension',
            'date_create', 'date_last_modify', 'is_public', 'folder', 'size'
        ]
        super(TrackerFolderList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        if 'type' in self.kwargs and self.kwargs['type'] != 'company':
            list_method = 'list_{}_folders'.format(self.kwargs['type'])
            project = Project.objects.get(id=self.kwargs['pk'])
            self.queryset = getattr(profile, list_method)(project=project).filter(is_root=True).distinct()
        else:
            self.queryset = profile.list_company_folders().filter(is_root=True).distinct()
        return super(TrackerFolderList, self).get_queryset()

class TrackerFolderDetailView(
    TrackerFolderMixin,
    generics.RetrieveAPIView):
    """
    Get a single video
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.FolderSerializer

    def __init__(self, *args, **kwargs):
        self.folder_response_include_fields = [
             'id', 'title', 'folder', 'is_root',
            'extension', 'note', 'is_public', 'size', 'media'
        ]
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo', 'is_public',
            'tags', 'note', 'photo_64', 'extension', 'folder'
        ]
        self.video_response_include_fields = [
            'id', 'title', 'pub_date', 'video',
            'tags', 'note', 'extension', 'is_public', 'folder'
        ]
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document', 'extension',
            'date_create', 'date_last_modify', 'is_public', 'folder'
        ]
        super(TrackerFolderDetailView, self).__init__(*args, **kwargs)

full_path = ""

def get_folder_path(obj):
    global full_path
    if obj.parent:
        root_folder = obj.parent
        path = get_folder_path(root_folder)
        full_path += "/{}".format(path)
    else:
        path = obj.name
    return path


class TrackerFolderStructureList(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all company folders
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = FolderStructureSerializer

    def __init__(self, *args, **kwargs):
        self.folder_response_include_fields = [
            'id', 'title', 'folder', 'is_root',
            'extension', 'note', 'is_public', 'size', 'media'
        ]
        super(TrackerFolderStructureList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        if 'type' in self.kwargs and self.kwargs['type'] != 'company':
            list_method = 'list_{}_folders'.format(self.kwargs['type'])
            project = Project.objects.get(id=self.kwargs['pk'])
            self.queryset = getattr(profile, list_method)(project=project).filter().distinct()
        else:
            self.queryset = profile.list_company_folders().filter().distinct()
        return super(TrackerFolderStructureList, self).get_queryset()

    def list(self, request, *args, **kwargs):
        full_list = []
        queryset = self.get_queryset()
        for folder in queryset:
            global full_path
            full_path = ""
            get_folder_path(folder)
            full_list.append({
                'path': (full_path + '/{}'.format(folder.name)).split('/', 1)[1],
                'name': folder.name,
                'id': folder.id,
                'parent': folder.parent.id if folder.parent else None
            })
        return Response(data=full_list, status=status.HTTP_200_OK)


def get_upload_folder_path2(instance, subpath, folder, is_public, create=False, type='photo'):
    media_dir1 = instance._meta.model_name
    media_dir2 = slugify(instance.__str__().lower())
    if media_dir1 == 'project':
        media_dir1 = 'project'
        media_dir2 = instance.pk
    media_root = get_media_root(is_public)
    if create:
        if subpath == '' or subpath == '/':
            os.makedirs(os.path.join(media_root, type, format(media_dir1), format(media_dir2), folder))
        else:
            os.makedirs(os.path.join(media_root, type, format(media_dir1), format(media_dir2), subpath, folder))

    return os.path.join(media_root, type, format(media_dir1), format(media_dir2))


# class TrackerFolderDeleteView(generics.DestroyAPIView):
#     """
#     Delete a company photo
#     """
#     permission_classes = (RoleAccessPermission,)
#     permission_roles = (settings.OWNER, settings.DELEGATE,)
#
#     def delete(self, request, *args, **kwargs):
#         folder_name = self.request.query_params.get('name')
#         if folder_name:
#             content_type = ContentType.objects.get(model=self.kwargs['type'])
#             model_name = content_type.model
#             if model_name == 'company':
#                 generic_model = profile_models.Company
#             elif model_name == 'project':
#                 generic_model = project_models.Project
#             elif model_name == 'bom':
#                 generic_model = quotation_models.Bom
#             else:
#                 raise ValidationError("Model Not Found")
#
#             if not generic_model.objects.filter(pk=self.kwargs['pk']):
#                 raise ValidationError("Object Not Found")
#
#             if model_name == 'project':
#                 gen_mod = Project.objects.get(id=self.kwargs['pk'])
#             elif model_name == 'company':
#                 gen_mod = Company.objects.get(id=self.kwargs['pk'])
#             elif model_name == 'bom':
#                 gen_mod = Bom.objects.get(id=self.kwargs['pk'])
#             for type in ['photo', 'video', 'document']:
#                 company_folder = get_upload_folder_path2(gen_mod, '', '', False, False, type)
#                 if company_folder == False:
#                     return Response(status=status.HTTP_400_BAD_REQUEST, data={
#                         'error': 'Folder not created. Max subfolders limit is 3'
#                     })
#                 try:
#                     shutil.rmtree(os.path.join(company_folder, folder_name))  # remove dir and all contains
#                 except Exception as e:
#                     continue
#             return Response(status=status.HTTP_200_OK, data="Folder deleted successfully")
#         else:
#             return Response(status=status.HTTP_400_BAD_REQUEST, data="Enter a folder name for deleting one")
#

class TrackerFolderAddView(
    WhistleGenericViewMixin,
    TrackerFolderMixin,
    generics.CreateAPIView):
    """
    Add a single video
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.FolderAddSerializer

    def __init__(self, *args, **kwargs):
        self.folder_request_include_fields = [
            'content_type', 'object_id', 'name', 'is_public', 'is_root', 'parent'
        ]
        self.folder_response_include_fields = [
            'id', 'name', 'is_public', 'is_root', 'content_type', 'object_id', 'parent'
        ]
        super(TrackerFolderAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True
        request.data['content_type'] = ContentType.objects.get(model=self.kwargs['type']).id
        request.data['object_id'] = self.kwargs['pk']
        return self.create(request, *args, **kwargs)


class TrackerFolderEditView(
    WhistleGenericViewMixin,
    TrackerFolderMixin,
    generics.RetrieveUpdateAPIView):
    """
    Edit a company video
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.FolderEditSerializer

    def __init__(self, *args, **kwargs):
        self.folder_request_include_fields = [
            'name', 'parent', 'is_public', 'is_root'
        ]
        self.folder_response_include_fields = [
            'id', 'name', 'parent', 'is_public', 'is_root'
        ]
        self.video_response_include_fields = [
            'id', 'title', 'pub_date', 'video',
            'tags', 'note', 'extension', 'is_public', 'folder'
        ]
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document',
            'date_create', 'date_last_modify', 'status',
        ]
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo', 'is_public',
            'tags', 'note', 'photo_64', 'extension', 'folder'
        ]
        super(TrackerFolderEditView, self).__init__(*args, **kwargs)


class TrackerFolderDeleteView(
    TrackerFolderMixin,
    generics.RetrieveDestroyAPIView):
    """
    Delete a company video
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.FolderSerializer

    def __init__(self, *args, **kwargs):
        self.folder_response_include_fields = ['id', 'name', 'parent', 'is_public', 'is_root']
        super(TrackerFolderDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_folder(instance)
