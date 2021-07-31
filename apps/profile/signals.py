# -*- coding: utf-8 -*-

import os
import copy

from django.core.mail import send_mail
from django.template import Context
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from . import models as profile_models
from apps.notify import models as notify_models
from web.core.middleware.thread_local import get_current_profile
from web.core.utils import get_html_message, get_bell_notification_status, get_email_notification_status


@receiver([post_save, post_delete], sender=profile_models.Profile)
@receiver([post_save, post_delete], sender=profile_models.OwnerProfile)
@receiver([post_save, post_delete], sender=profile_models.DelegateProfile)
@receiver([post_save, post_delete], sender=profile_models.Level1Profile)
@receiver([post_save, post_delete], sender=profile_models.Level2Profile)
@receiver([post_save, post_delete], sender=profile_models.PhantomProfile)
def profile_notification(sender, instance, **kwargs):
    company_staff = []
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        if 'created' in kwargs:
            if not kwargs['created']:
                if not profile:
                    profile = instance

    if not profile:
        return

    try:
        if not instance.user and instance.email:
            if instance.__create:
                registration_link = os.path.join(settings.PROTOCOL + '://', settings.BASE_URL, 'pages/auth/register')
                from_mail = settings.NOTIFY_NOTIFY_NO_REPLY_EMAIL
                subject = _('Your email is added to EdilCloud')
                context = {
                    'logo_url': os.path.join(
                        settings.PROTOCOL + '://',
                        settings.BASE_URL,
                        'assets/images/logos/fuse.svg'
                    ),
                    'recipient_first_name': instance.first_name,
                    'recipient_last_name': instance.last_name,
                    'recipient_email': instance.email,
                    'company_name': instance.company.name,
                    'registration_page': registration_link
                }

                lang = instance.language if instance.language else 'en'

                # Text message
                text_message = render_to_string('profile/profile/email/registration_phantom_request_{}.txt'.format(
                    lang), context)

                # Html message
                html_message = render_to_string('profile/profile/email/registration_phantom_request_{}.html'.format(
                    lang), context)

                try:
                    send_mail(
                        subject=subject,
                        message=text_message,
                        html_message=html_message,
                        recipient_list=[instance.email],
                        from_email=from_mail,
                    )
                except Exception as e:
                    print(e)

        else:
            endpoint = os.path.join(settings.PROTOCOL + '://', settings.BASE_URL, 'profile')
            content = "Mr <strong>%s %s</strong> have created this event. " % (profile.first_name, profile.last_name)
            if 'created' in kwargs:
                if kwargs['created']:
                    if instance.company_invitation_date:
                        company_staff = [instance]
                        subject = _('New invitation from company (%s) '% instance.company.name)
                    else:
                        company_staff = instance.company.get_owners_and_delegates()
                        subject = _('New invitation from staff (%s) (%s) '% (instance.first_name, instance.last_name))
                        endpoint = os.path.join(settings.PROTOCOL + '://', settings.BASE_URL, 'organico')
                else:
                    # Todo: beautify the following logic
                    old_obj = copy.deepcopy(instance._Profile__original_instance)
                    instance.__dict__.pop('_Profile__original_instance', None)
                    new_obj = instance.__dict__

                    diffkeys = []

                    for key, value in old_obj.items():
                        if value != new_obj[key]:
                            diffkeys.append(key)

                    invitations_type = ['invitation_refuse_date', 'company_invitation_date', 'profile_invitation_date']
                    if any(x in invitations_type for x in diffkeys):

                        get_types = list(set(invitations_type) & set(diffkeys))
                        if get_types:
                            if len(get_types) >= 2:
                                if all(x in ['invitation_refuse_date', 'company_invitation_date'] for x in get_types):
                                    company_staff = [instance]
                                    subject = _('Invitation reaccepted by company (%s) ' % instance.company.name)
                                elif all(x in ['invitation_refuse_date', 'profile_invitation_date'] for x in get_types):
                                    company_staff = instance.company.get_owners_and_delegates()
                                    subject = _('Invitation reaccepted by staff (%s) (%s) ' % (instance.first_name, instance.last_name))
                                else:
                                    return
                            else:
                                if get_types[0] == 'invitation_refuse_date':
                                    if not instance.company_invitation_date:
                                        company_staff = [instance]
                                        subject = _('Invitation refused by company (%s) ' % instance.company.name)
                                    else:
                                        company_staff = instance.company.get_owners_and_delegates()
                                        subject = _(
                                            'Invitation refused by staff (%s) (%s) ' % (instance.first_name, instance.last_name))
                                        endpoint = os.path.join(settings.PROTOCOL + '://', settings.BASE_URL, 'organico')
                                elif get_types[0] == 'company_invitation_date':
                                    company_staff = [instance]
                                    subject = _('Invitation accepted by company (%s) ' % instance.company.name)
                                elif get_types[0] == 'profile_invitation_date':
                                    company_staff = instance.company.get_owners_and_delegates()
                                    subject = _('Invitation accepted by staff (%s) (%s) '% (instance.first_name, instance.last_name))
                                else:
                                    return
                        else:
                            return
                    else:
                        company_staff = profile_models.Profile.objects.filter(pk=instance.id).union(
                            instance.company.get_owners_and_delegates()
                        )
                        subject = _('Profile (%s %s) information has been changed by company (%s)'% (instance.first_name, instance.last_name, instance.company.name))
                        endpoint = os.path.join(settings.PROTOCOL + '://', settings.BASE_URL, 'organico')
            else:
                company_staff = profile_models.Profile.objects.filter(id=instance.id).union(
                    instance.company.get_owners_and_delegates()
                )
                subject = _('Profile (%s %s) deleted by company (%s)'% (instance.first_name, instance.last_name, instance.company.name))
                endpoint = os.path.join(settings.PROTOCOL + '://', settings.BASE_URL, 'organico')

            final_content = "For simplicity, the following button will redirect to the target page."
            body = get_html_message(content, final_content, endpoint)
            type = ContentType.objects.get(model='profile')

            notify_obj = notify_models.Notify.objects.create(
                sender=profile, subject=subject, body=body,
                content_type=type, object_id=instance.id,
                creator=profile.user, last_modifier=profile.user
            )

            recipient_objs = []

            for staff in company_staff:
                bell_status = get_bell_notification_status(
                    staff, 'profile'
                )
                email_status = get_email_notification_status(
                    staff, 'profile'
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


@receiver([pre_save], sender=profile_models.Profile)
@receiver([pre_save], sender=profile_models.OwnerProfile)
@receiver([pre_save], sender=profile_models.DelegateProfile)
@receiver([pre_save], sender=profile_models.Level1Profile)
@receiver([pre_save], sender=profile_models.Level2Profile)
@receiver([pre_save], sender=profile_models.PhantomProfile)
def profile_pre_save(sender, instance, **kwargs):
    if instance.id:
        instance.__create = False
    else:
        instance.__create = True


@receiver([post_save, post_delete], sender=profile_models.Partnership)
def partnership_notification(sender, instance, **kwargs):
    company_staff = []
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        return

    try:
        content = "Mr <strong>%s %s</strong> have created this event. " % (profile.first_name, profile.last_name)

        if 'created' in kwargs:
            if kwargs['created']:
                subject = _('New Partnership request from company (%s)'% instance.guest_company.name)
                company_staff = instance.inviting_company.get_owners_and_delegates()
            else:
                subject = _('Partnership proposal accepted by company (%s)' % instance.inviting_company.name)
                company_staff = instance.guest_company.get_owners_and_delegates()
        else:
            subject = _('Partnership proposal rejected by company (%s)' % instance.inviting_company.name)
            company_staff = instance.guest_company.get_owners_and_delegates()

        final_content = "For simplicity, the following button will redirect to the target page."
        body = get_html_message(content, final_content, os.path.join(settings.PROTOCOL+'://', settings.BASE_URL, 'imprese'))
        type = ContentType.objects.get(model=sender.__name__.lower())

        notify_obj = notify_models.Notify.objects.create(
            sender=profile, subject=subject, body=body,
            content_type=type, object_id=instance.id,
            creator=profile.user, last_modifier=profile.user
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


@receiver([post_save, post_delete], sender=profile_models.Favourite)
def follow_notification(sender, instance, **kwargs):
    company_staff = []
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        return

    try:
        content = "Mr <strong>%s %s</strong> have created this event. " % (profile.first_name, profile.last_name)

        if 'created' in kwargs:
            if kwargs['created']:
                subject = _('New Follow request from company (%s)' % instance.company.name)
                company_staff = instance.company_followed.get_owners_and_delegates()
            else:
                subject = _('Follow proposal accepted by company (%s)' % instance.company_followed.name)
                company_staff = instance.company.get_owners_and_delegates()
        else:
            subject = _('Follow proposal rejected by company (%s)' % instance.company_followed.name)
            company_staff = instance.company.get_owners_and_delegates()

        final_content = "For simplicity, the following button will redirect to the target page."
        body = get_html_message(content, final_content, os.path.join(settings.PROTOCOL+'://', settings.BASE_URL, 'imprese'))
        type = ContentType.objects.get(model=sender.__name__.lower())

        notify_obj = notify_models.Notify.objects.create(
            sender=profile, subject=subject, body=body,
            content_type=type, object_id=instance.id,
            creator=profile.user, last_modifier=profile.user
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


@receiver([post_save], sender=profile_models.Sponsor)
def sponsor_request_notification(sender, instance, **kwargs):
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        return

    if instance.status == 1 and instance.__old_status != 1:
        from_mail = settings.NOTIFY_NOTIFY_NO_REPLY_EMAIL
        subject = _('Your request of sponsor has been accepted')

        tags = ''
        for key, value in instance.tags.items():
            tags = "{}, {}".format(value['name'], tags)
        recipients = instance.company.get_active_owners()
        for recipient in recipients:
            context = {
                'logo_url': os.path.join(
                    settings.PROTOCOL + '://',
                    settings.BASE_URL,
                    'assets/images/logos/fuse.svg'
                ),
                'recipient_first_name': recipient.first_name,
                'recipient_last_name': recipient.last_name,
                'tags': tags,
                'expiration_date': instance.expired_date,
            }

            lang = recipient.language if recipient.language else 'en'

            # Text message
            text_message = render_to_string('profile/profile/email/sponsor_accepted_{}.txt'.format(
                lang), context)

            # Html message
            html_message = render_to_string('profile/profile/email/sponsor_accepted_{}.html'.format(
                lang), context)


            try:
                send_mail(
                    subject=subject,
                    message=text_message,
                    html_message=html_message,
                    recipient_list=[recipient.email],
                    from_email=from_mail,
                )
            except Exception as e:
                    print(e)

    if instance.status == 2:
        from_mail = settings.NOTIFY_NOTIFY_NO_REPLY_EMAIL
        context = {
            'logo_url': os.path.join(
                settings.PROTOCOL + '://',
                settings.BASE_URL,
                'assets/images/logos/fuse.svg'
            ),
            'owner_name': '{} {}'.format(profile.first_name, profile.last_name),
            'recipient_first_name': profile.first_name,
            'recipient_last_name': profile.last_name,
            'company_name': instance.company.name,
            'company_mobile': profile.mobile if profile.mobile else instance.company.phone,
            'company_phone': profile.phone if profile.phone else instance.company.phone,
            'company_email': profile.email if profile.email else instance.company.email,
            'company_url': instance.company.url
        }
        # Text message
        text_message = render_to_string('profile/profile/email/sponsor_request.txt', context)
        # Html message
        html_message = render_to_string('profile/profile/email/sponsor_request.html', context)
        try:
            send_mail(
                subject='Nuova richiesta sponsor',
                message=text_message,
                html_message=html_message,
                recipient_list=[settings.NEW_SPONSOR_REQUEST_RECIPIENT],
                from_email=from_mail,
            )
        except Exception as e:
                print(e)


@receiver([pre_save], sender=profile_models.Sponsor)
def save_old_status(sender, instance, **kwargs):
    instance.__old_status = None
    if instance.id:
        orig = profile_models.Sponsor.objects.get(id=instance.id)
        instance.__old_status = orig.status
