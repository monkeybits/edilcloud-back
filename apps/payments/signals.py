import json
import emoji
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from apps.notify.signals import send_push_notification
from apps.notify import models as notify_models
from web.core.middleware.thread_local import get_current_profile
from web.core.utils import get_bell_notification_status, get_email_notification_status


def payment_success_notification(senders):
    profile = senders[0]
    try:
        subject = '%s ' % emoji.emojize(':credit_card:') + _(
            "Payment Success").__str__()
        content = '%s ' % emoji.emojize(':credit_card:') + _(
            "Payment Success for company:").__str__() + " %s" + profile.company.name
        endpoint = '/apps/todo/all/'
        body = json.dumps({
            'content': content,
            'url': endpoint
        })
        type = ContentType.objects.get(model='profile')

        for sender in senders:
            notify_obj = notify_models.Notify.objects.create(
                sender=profile, subject=subject, body=body,
                content_type=type, object_id=profile.id,
                creator=profile.user, last_modifier=profile.user
            )

            bell_status = get_bell_notification_status(
                sender, 'profile'
            )
            email_status = get_email_notification_status(
                sender, 'profile'
            )
            translation.activate(profile.user.get_main_profile().language)

            if bell_status or email_status:
                notify_recipient = notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=sender,
                    creator=profile.user, last_modifier=profile.user)
                notify_recipient.save()
                send_push_notification(notify_obj, sender, subject, body)
    except Exception as e:
        print(e)


def payment_failed_notification(senders):
    profile = senders[0]
    try:
        subject = '%s ' % emoji.emojize(':credit_card:') + _(
            "Payment Failed").__str__()
        content = '%s ' % emoji.emojize(':credit_card:') + _(
            "Payment Failed for company:").__str__() + " %s" + profile.company.name
        endpoint = '/apps/companies/'
        body = json.dumps({
            'content': content,
            'url': endpoint
        })
        type = ContentType.objects.get(model='profile')

        for sender in senders:
            notify_obj = notify_models.Notify.objects.create(
                sender=profile, subject=subject, body=body,
                content_type=type, object_id=profile.id,
                creator=profile.user, last_modifier=profile.user
            )

            bell_status = get_bell_notification_status(
                sender, 'profile'
            )
            email_status = get_email_notification_status(
                sender, 'profile'
            )
            translation.activate(profile.user.get_main_profile().language)

            if bell_status or email_status:
                notify_recipient = notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=sender,
                    creator=profile.user, last_modifier=profile.user)
                notify_recipient.save()
                send_push_notification(notify_obj, sender, subject, body)
    except Exception as e:
        print(e)
