# -*- coding: utf-8 -*-

import os

from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from . import models as document_models
from apps.notify import models as notify_models
from web.core.middleware.thread_local import get_current_profile
from web.core.utils import get_html_message, get_bell_notification_status, get_email_notification_status


@receiver([post_save, post_delete], sender=document_models.Document)
def document_notification(sender, instance, **kwargs):
    company_staff = []
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        return

    try:
        endpoint = os.path.join(settings.PROTOCOL+'://', settings.BASE_URL, 'dashboard')
        if instance.content_type.name == 'company':
            company_staff = instance.content_object.profiles.all()
            title = instance.content_object.name
        elif instance.content_type.name == 'project':
            # Level 1 project
            if instance.content_object.shared_project:
                level1_project = instance.content_object.shared_project.profiles.all().union(
                    instance.content_object.shared_project.company.get_owners_and_delegates()
                )
                company_staff = instance.content_object.profiles.all().union(
                    instance.content_object.company.get_owners_and_delegates(),
                    level1_project
                )
            else:
                company_staff = instance.content_object.profiles.all().union(
                    instance.content_object.company.get_owners_and_delegates()
                )
            endpoint = os.path.join(settings.PROTOCOL+'://', settings.BASE_URL, 'project/%s' % instance.object_id)
            title = instance.content_object.name
        elif instance.content_type.name == 'bom':
            company_staff = instance.content_object.owner.profiles.all()
            endpoint = os.path.join(settings.PROTOCOL+'://', settings.BASE_URL, 'preventivi')
            title = instance.content_object.title

        content = "Mr <strong>%s %s</strong> have created this event. " % (profile.first_name, profile.last_name)

        if 'created' in kwargs:
            if kwargs['created']:
                subject = _('New Document (%s) created in %s (%s)' % (instance.title, instance.content_type.name, title))
            else:
                subject = _('Document (%s) updated in %s (%s)' % (instance.title, instance.content_type.name, title))
        else:
            subject = _('Document (%s) deleted in %s (%s)' % (instance.title, instance.content_type.name, title))

        final_content = "For simplicity, the following button will redirect to the target page."
        body = get_html_message(content, final_content, endpoint)
        type = ContentType.objects.get(model=instance.content_type.name.lower())

        notify_obj = notify_models.Notify.objects.create(
            sender=profile, subject=subject, body=body,
            content_type=type, object_id=instance.object_id,
            creator=profile.user, last_modifier=profile.user
        )

        recipient_objs = []

        for staff in company_staff:
            bell_status = get_bell_notification_status(
                staff, instance.content_type.name
            )
            email_status = get_email_notification_status(
                staff, instance.content_type.name
            )

            if bell_status or email_status:
                recipient_objs.append(notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=staff,
                    creator=profile.user, last_modifier=profile.user)
                )

        notify_models.NotificationRecipient.objects.bulk_create(
            recipient_objs,
            batch_size=100
        )
    except Exception as e:
        print(e)
