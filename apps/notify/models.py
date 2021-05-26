# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from apps.profile.models import Profile
from web.core.models import UserModel, DateModel, OrderedModel, CleanModel, StatusModel


def notify_limit_choices_to():
    q_objects = models.Q()
    for key, value in enumerate(settings.NOTIFY_CONTENT_TYPE_LIMIT_CHOICES_TO):
        q_objects.add(models.Q(app_label=value['app_label'], model=value['model']), models.Q.OR)
    return q_objects


@python_2_unicode_compatible
class Notify(CleanModel, UserModel, DateModel, OrderedModel):
    recipients = models.ManyToManyField(
        'profile.Profile',
        through='NotificationRecipient',
        related_name='recipients',
        verbose_name=_('recipients'),
    )
    sender = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='notifications_sender',
        verbose_name=_('sender'),
    )
    subject = models.CharField(
        max_length=255,
        verbose_name=_('subject'),
    )
    body = models.TextField(
        blank=True,
        verbose_name=_('body'),
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='notifications',
        limit_choices_to=notify_limit_choices_to
    )
    object_id = models.PositiveIntegerField()

    class Meta:
        verbose_name = _('notify')
        verbose_name_plural = _('notifies')
        permissions = (
            ("list_notify", "can list notify"),
            ("detail_notify", "can detail notify"),
            ("disable_notify", "can disable notify"),
        )
        ordering = ['-date_create']
        get_latest_by = "date_create"

    def __str__(self):
        return '{}: {}'.format(self.sender, self.subject)

    @classmethod
    def get_notifications(cls):
        return cls.objects.all()


@python_2_unicode_compatible
class NotificationRecipient(UserModel, DateModel, StatusModel):
    recipient = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='notification_recipient',
        verbose_name=_('recipient'),
    )
    notification = models.ForeignKey(
        Notify,
        on_delete=models.CASCADE,
        related_name='notification_recipient',
        verbose_name=_('notification'),
    )
    is_email = models.BooleanField(
        default=False,
        verbose_name=_('is email')
    )
    is_notify = models.BooleanField(
        default=False,
        verbose_name=_('is notify')
    )
    is_email_sent = models.BooleanField(
        default=False,
        verbose_name=_('is email sent')
    )
    reading_date = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_('reading date')
    )

    class Meta:
        verbose_name = _('notification recipient')
        verbose_name_plural = _('notification recipients')
        permissions = (
            ("list_notificationrecipient", "can list notification recipient"),
            ("detail_notificationrecipient", "can detail notification recipient"),
            ("disable_notificationrecipient", "can disable notification recipient"),
        )
        unique_together = (('recipient', 'notification',),)
        ordering = ['-date_create']
        get_latest_by = "date_create"

    def __str__(self):
        return '{}: {}'.format(self.recipient, self.notification)

    def send_notify_email(self):
        if not self.is_email_sent and self.is_email:
            from_mail = settings.NOTIFY_NOTIFY_NO_REPLY_EMAIL

            endpoint = os.path.join(settings.PROTOCOL+':/', settings.BASE_URL, 'dashboard')
            if self.notification.content_type.name in ['project', 'task', 'team', 'activity']:
                endpoint = os.path.join(settings.PROTOCOL+':/', settings.BASE_URL, 'project/%s' % self.notification.object_id)
            elif self.notification.content_type.name == 'bom':
                endpoint = os.path.join(settings.PROTOCOL+':/', settings.BASE_URL, 'preventivi')

            context = {
                'logo_url': os.path.join(
                    settings.PROTOCOL + '://',
                    settings.BASE_URL,
                    'assets/images/logos/fuse.svg'
                ),
                "first_name": self.recipient.first_name,
                "last_name": self.recipient.last_name,
                "company_name": self.recipient.company.name,
                "info_phrase": self.notification.subject,
                "endpoint": endpoint,
                'base_url': settings.BASE_URL,
                "protocol": settings.PROTOCOL,
                "subject": self.notification.subject
            }

            language = self.recipient.language if self.recipient.language else 'en'
            # Text message
            text_message = render_to_string('notify/notify/email/notification_email_{}.txt'.format(
                language), context)

            # Html message
            html_message = render_to_string('notify/notify/email/notification_email_{}.html'.format(
                language), context)
            try:
                send_mail(
                    subject=_('Whistle ') + self.notification.subject,
                    message=text_message,
                    html_message=html_message,
                    recipient_list=[self.recipient.email],
                    from_email=from_mail,
                )
                self.is_email_sent = True
                self.save()
            except Exception as e:
                print(e)
