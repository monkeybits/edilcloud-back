# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from web.core.models import UserModel, DateModel, StatusModel, OrderedModel, CleanModel

def get_upload_message_file_path(instance, filename):
    talk = instance.message.talk.id
    return os.path.join(u"talks", u"{0}".format(str(talk)), "messages", str(instance.message.id), filename)


def talk_limit_choices_to():
    q_objects = models.Q()
    for key, value in enumerate(settings.MESSAGE_TALK_CONTENT_TYPE_LIMIT_CHOICES_TO):
        q_objects.add(models.Q(app_label=value['app_label'], model=value['model']), models.Q.OR)
    return q_objects


@python_2_unicode_compatible
class Talk(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    code = models.CharField(
        max_length=32,
        verbose_name=_('code')
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='talks',
        limit_choices_to=talk_limit_choices_to
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    for_concrete_model = models.BooleanField(
        default=False,
        verbose_name=_('for concrete model'),
    )

    class Meta:
        verbose_name = _('talk')
        verbose_name_plural = _('talks')
        permissions = (
            ("list_talk", "can list talk"),
            ("detail_talk", "can detail talk"),
            ("disable_talk", "can disable talk"),
        )
        ordering = ['date_create']
        get_latest_by = "date_create"

    def __str__(self):
        return '{}: {}: {}'.format(self.code, self.content_type, self.object_id)

    def save(self, *args, **kwargs):
        if not self.id:
            self.code = get_random_string(length=32)
        return super(Talk, self).save(*args, **kwargs)

    @property
    def get_messages_count(self):
        return self.messages.count()

    get_messages_count.fget.short_description = _('Messages')

    def get_content_type_model(self):
        return self.content_type.model


@python_2_unicode_compatible
class Message(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    body = models.TextField(
        verbose_name=_('body')
    )
    talk = models.ForeignKey(
        Talk,
        related_name='messages',
        on_delete=models.CASCADE,
        verbose_name=_('talk')
    )
    sender = models.ForeignKey(
        'profile.Profile',
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('sender'),
    )

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        permissions = (
            ("list_message", "can list message"),
            ("detail_message", "can detail message"),
            ("disable_message", "can disable message"),
        )
        ordering = ['date_create']
        get_latest_by = "date_create"

    def __str__(self):
        return '{} - {}: {}'.format(self.body, self.talk, self.sender)

    @classmethod
    def get_messages(cls):
        return cls.objects.all()

@python_2_unicode_compatible
class MessageFileAssignment(OrderedModel):
    media = models.FileField(blank=True, default="", upload_to=get_upload_message_file_path)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('message file assignment')
        verbose_name_plural = _('message filedocker assignments')