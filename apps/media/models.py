# # -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import pathlib

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from web.core.models import UserModel, DateModel, StatusModel, OrderedModel, CleanModel
from web.api.views import get_media_root

photo_fs = FileSystemStorage(location=settings.BASE_DIR, base_url="/")
video_fs = FileSystemStorage(location=settings.BASE_DIR, base_url="/")


def get_upload_photo_path(instance, filename):
    media_dir1 = instance.content_object._meta.model_name
    media_dir2 = slugify(instance.content_object.__str__().lower())
    ext = pathlib.Path(filename).suffix
    if hasattr(instance, 'title'):
        filename = '{}{}'.format(slugify(instance.title), ext)
    media_root = get_media_root(instance.is_public)
    if hasattr(instance, 'additional_path'):
        return os.path.join(media_root, 'photo', format(media_dir1), format(media_dir2), instance.additional_path, filename)

    return os.path.join(media_root, 'photo', format(media_dir1), format(media_dir2), filename)


def get_upload_video_path(instance, filename):
    media_dir1 = instance.content_object._meta.model_name
    media_dir2 = slugify(instance.content_object.__str__().lower())
    ext = pathlib.Path(filename).suffix
    filename = '{}{}'.format(slugify(instance.title), ext)
    media_root = get_media_root(instance.is_public)
    if hasattr(instance, 'additional_path'):
        return os.path.join(media_root, 'video', format(media_dir1), format(media_dir2), instance.additional_path,
                            filename)
    return os.path.join(media_root, 'video',format(media_dir1), format(media_dir2), filename)


def photo_limit_choices_to():
    q_objects = models.Q()
    for key, value in enumerate(settings.MEDIA_PHOTO_CONTENT_TYPE_LIMIT_CHOICES_TO):
        q_objects.add(models.Q(app_label=value['app_label'], model=value['model']), models.Q.OR)
    return q_objects


def video_limit_choices_to():
    q_objects = models.Q()
    for key, value in enumerate(settings.MEDIA_VIDEO_CONTENT_TYPE_LIMIT_CHOICES_TO):
        q_objects.add(models.Q(app_label=value['app_label'], model=value['model']), models.Q.OR)
    return q_objects


@python_2_unicode_compatible
class Photo(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=photo_limit_choices_to
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    for_concrete_model = models.BooleanField(
        default=False,
        verbose_name=_('for concrete model'),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('title'),
    )
    pub_date = models.DateField(
        blank=True, null=True,
        verbose_name=_('publication date'),
    )
    photo = models.ImageField(
        storage=photo_fs,
        max_length=1000,
        upload_to=get_upload_photo_path,
        verbose_name=_('image')
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name=_('is public')
    )
    note = models.TextField(
        blank=True,
        verbose_name=_('note'),
    )
    tags = ArrayField(
        models.CharField(
            max_length=255, blank=True
        ),
        blank=True, null=True,
    )

    class Meta:
        verbose_name = _('photo')
        verbose_name_plural = _('photos')
        permissions = (
            ("list_photo", "can list photo"),
            ("detail_photo", "can detail photo"),
            ("disable_photo", "can disable photo"),
        )
        ordering = ['-date_last_modify']
        get_latest_by = "date_create"

    def __str__(self):
        return '{} {}: {}'.format(
            self.content_object._meta.model_name,
            self.content_object.__str__(),
            self.title
        )

    def get_file_extension(self):
        name, extension = os.path.splitext(self.photo.name)
        return extension


@python_2_unicode_compatible
class Video(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=photo_limit_choices_to
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    for_concrete_model = models.BooleanField(
        default=False,
        verbose_name=_('for concrete model'),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('title'),
    )
    pub_date = models.DateField(
        blank=True, null=True,
        verbose_name=_('publication date'),
    )
    video = models.FileField(
        storage=video_fs,
        max_length=1000,
        upload_to=get_upload_video_path,
        verbose_name=_('video'),
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name=_('is public')
    )
    note = models.TextField(
        blank=True,
        verbose_name=_('note'),
    )
    tags = ArrayField(
        models.CharField(
            max_length=255, blank=True
        ),
        blank=True, null=True,
    )

    class Meta:
        verbose_name = _('video')
        verbose_name_plural = _('videos')
        permissions = (
            ("list_video", "can list video"),
            ("detail_video", "can detail video"),
            ("disable_video", "can disable video"),
        )
        ordering = ['-date_last_modify']
        get_latest_by = "date_create"

    def __str__(self):
        return '{} {}: {}'.format(
            self.content_object._meta.model_name,
            self.content_object.__str__(),
            self.title
        )

    def get_file_extension(self):
        name, extension = os.path.splitext(self.video.name)
        return extension
