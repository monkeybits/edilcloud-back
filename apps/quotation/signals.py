# -*- coding: utf-8 -*-

import os

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from . import models as quotation_models
from apps.notify import models as notify_models
from web.core.middleware.thread_local import get_current_profile
from web.core.utils import get_html_message, get_bell_notification_status, get_email_notification_status


@receiver([post_save, post_delete], sender=quotation_models.Offer)
def offer_notification(sender, instance, **kwargs):
    company_staff = instance.owner.get_owners_and_delegates()
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        return

    try:
        content = "Mr <strong>%s %s</strong> have created this event. " % (profile.first_name, profile.last_name)
        if 'created' in kwargs:
            if kwargs['created']:
                subject = _('New offer (%s) created in company (%s)' % (instance.title, instance.owner.name))
            else:
                subject = _('Offer (%s) updated in company (%s)' % (instance.title, instance.owner.name))
        else:
            subject = _('Offer (%s) deleted in company (%s)' % (instance.title, instance.owner.name))

        final_content = "For simplicity, the following button will redirect to the target page."
        body = get_html_message(content, final_content, os.path.join(settings.PROTOCOL+'://', settings.BASE_URL, 'dashboard'))
        type = ContentType.objects.get(model=sender.__name__.lower())

        notify_obj = notify_models.Notify.objects.create(
            sender=profile, subject=subject, body=body,
            content_type=type, object_id=instance.id,
            creator=profile.user, last_modifier=profile.user,
        )

        recipient_objs = []

        for staff in company_staff:
            bell_status = get_bell_notification_status(
                staff, sender.__name__.lower()
            )
            email_status = get_email_notification_status(
                staff, sender.__name__.lower()
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


@receiver([post_save, post_delete], sender=quotation_models.Bom)
def bom_notification(sender, instance, **kwargs):
    company_staff = instance.owner.get_owners_and_delegates()
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        return

    try:
        content = "Mr <strong>%s %s</strong> have created this event. " % (profile.first_name, profile.last_name)
        if 'created' in kwargs:
            if kwargs['created']:
                subject = _('New Bom (%s) created in company (%s)' % (instance.title, instance.owner.name))
            else:
                subject = _('Bom (%s) updated in company (%s)' % (instance.title, instance.owner.name))
        else:
            subject = _('Bom (%s) deleted in company (%s)' % (instance.title, instance.owner.name))

        final_content = "For simplicity, the following button will redirect to the target page."
        body = get_html_message(content, final_content, os.path.join(settings.PROTOCOL+'://', settings.BASE_URL, 'preventivi'))
        type = ContentType.objects.get(model=sender.__name__.lower())

        notify_obj = notify_models.Notify.objects.create(
            sender=profile, subject=subject, body=body,
            content_type=type, object_id=instance.id,
            creator=profile.user, last_modifier=profile.user,
        )

        recipient_objs = []

        for staff in company_staff:
            bell_status = get_bell_notification_status(
                staff, sender.__name__.lower()
            )
            email_status = get_email_notification_status(
                staff, sender.__name__.lower()
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


@receiver([post_save], sender=quotation_models.BoughtOffer)
def bought_offer_notification(sender, instance, **kwargs):
    company_staff = instance.offer.owner.get_owners_and_delegates()
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        return

    try:
        if 'created' in kwargs:
            if kwargs['created']:
                subject_en = _('Offer (%s) bought' % (instance.offer.title))
                subject_it = _('Acquisto vostra offerta (%s)' % (instance.offer.title))
                content_en = "Mr <strong>%s %s</strong> have bought your offer <strong>%s</strong>. " % (
                                profile.first_name, profile.last_name, instance.offer.title)
                final_content_en = '''<p>Please contact <strong>%s %s </strong> for further informations.<br><br>
                                   <strong>Company:</strong> %s<br>
                                   <strong>Mobile:</strong> %s<br>
                                   <strong>Tel:</strong> %s<br>
                                   <strong>Email:</strong> %s<br>
                                   <strong>WWW:</strong> %s<br></p>''' % (profile.first_name, profile.last_name,
                                        profile.company.name, profile.mobile, profile.phone, profile.email,
                                        profile.company.url)
                content_it = "<strong>%s %s</strong> ha acquistato la vostra offerta <strong>%s</strong>. " % (
                    profile.first_name, profile.last_name, instance.offer.title)
                final_content_it = '''<p>Si prega di contattare <strong>%s %s </strong> per ulteriori informazioni.<br>
                                       <br>
                                       <strong>Azienda:</strong> %s<br>
                                       <strong>Mobile:</strong> %s<br>
                                       <strong>Tel:</strong> %s<br>
                                       <strong>Email:</strong> %s<br>
                                       <strong>WWW:</strong> %s<br></p>''' % (
                                        profile.first_name, profile.last_name,
                                        profile.company.name, profile.mobile, profile.phone, profile.email,
                                        profile.company.url)

                body_en = get_html_message(content_en, final_content_en)
                body_it = get_html_message(content_it, final_content_it)
                type = ContentType.objects.get(model=quotation_models.Offer.__name__.lower())

                it_recipient = company_staff.filter(language='it')

                en_recipient = company_staff.filter(~Q(language='it'))

                recipient_objs = []
                if it_recipient:
                    notify_obj = notify_models.Notify.objects.create(
                        sender=profile, subject=subject_it, body=body_it,
                        content_type=type, object_id=instance.id,
                        creator=profile.user, last_modifier=profile.user,
                    )
                    for staff in it_recipient:
                        bell_status = get_bell_notification_status(
                            staff, sender.__name__.lower()
                        )
                        email_status = get_email_notification_status(
                            staff, sender.__name__.lower()
                        )

                        if bell_status or email_status:
                            recipient_objs.append(notify_models.NotificationRecipient(
                                notification=notify_obj, is_email=email_status,
                                is_notify=bell_status, recipient=staff,
                                creator=profile.user, last_modifier=profile.user)
                            )

                if en_recipient:
                    notify_obj = notify_models.Notify.objects.create(
                        sender=profile, subject=subject_en, body=body_en,
                        content_type=type, object_id=instance.id,
                        creator=profile.user, last_modifier=profile.user,
                    )
                    for staff in en_recipient:
                        bell_status = get_bell_notification_status(
                            staff, sender.__name__.lower()
                        )
                        email_status = get_email_notification_status(
                            staff, sender.__name__.lower()
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
