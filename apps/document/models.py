# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import pathlib

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from apps.media.models import Folder
from web.core.models import UserModel, DateModel, StatusModel, OrderedModel, CleanModel
from web.api.views import get_media_root

from django.core.files.storage import FileSystemStorage

doc_fs = FileSystemStorage(location=settings.BASE_DIR, base_url="/")


def get_upload_document_path(instance, filename):
    # TODO tree upload
    media_dir1 = instance.content_object._meta.model_name
    if hasattr(instance.content_object, 'slug'):
        media_dir2 = instance.content_object.slug
    else:
        media_dir2 = instance.content_object.id
    ext = pathlib.Path(filename).suffix
    filename = '{}{}'.format(slugify(instance.title), ext)
    media_root = get_media_root(instance.is_public)
    if hasattr(instance, 'additional_path'):
        return os.path.join(media_root, 'document', format(media_dir1), format(media_dir2), instance.additional_path,
                            filename)
    return os.path.join(media_root, "document", format(media_dir1), format(media_dir2), filename)


def document_limit_choices_to():
    q_objects = models.Q()
    for key, value in enumerate(settings.DOCUMENT_DOCUMENT_CONTENT_TYPE_LIMIT_CHOICES_TO):
        q_objects.add(models.Q(app_label=value['app_label'], model=value['model']), models.Q.OR)
    return q_objects


@python_2_unicode_compatible
class Document(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=document_limit_choices_to
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
    description = models.TextField(
        verbose_name=_('description'),
    )
    document = models.FileField(
        storage=doc_fs,
        max_length=1000,
        upload_to=get_upload_document_path,
        verbose_name=_('certification'),
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name=_('is public')
    )
    folder = models.ForeignKey(
        Folder,
        null=True,
        on_delete=models.CASCADE
    )
    class Meta:
        verbose_name = _('document')
        verbose_name_plural = _('documents')
        permissions = (
            ("list_document", "can list document"),
            ("detail_document", "can detail document"),
            ("disable_document", "can disable document"),
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
        name, extension = os.path.splitext(self.document.name)
        return extension