# -*- coding: utf-8 -*-
import json
import os

from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from . import models as project_models
from apps.notify import models as notify_models
from web.core.middleware.thread_local import get_current_profile
from web.core.utils import get_html_message, get_bell_notification_status, get_email_notification_status


# @receiver([post_save, post_delete], sender=project_models.SharedProject)
# @receiver([post_save, post_delete], sender=project_models.InternalSharedProject)
# @receiver([post_save, post_delete], sender=project_models.GenericProject)
from ..notify.signals import send_push_notification


@receiver([post_save, post_delete], sender=project_models.Project)
def project_notification(sender, instance, **kwargs):
    company_staff = instance.profiles.all().union(
        instance.company.get_owners_and_delegates()
    )
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        return

    try:
        endpoint = '/apps/projects/{}'.format(str(instance.id))
        if 'created' in kwargs:
            if kwargs['created']:
                subject = _('New Project (%s) created in company (%s)'% (instance.name, instance.company.name))
            else:
                subject = _('Project (%s) updated in company (%s)'% (instance.name, instance.company.name))
        else:
            subject = _('Project (%s) deleted in company (%s)'% (instance.name, instance.company.name))

        body = json.dumps({
            'content': subject.__str__(),
            'url': endpoint
        })
        type = ContentType.objects.get(model=sender.__name__.lower())

        notify_obj = notify_models.Notify.objects.create(
            sender=profile, subject=subject, body=body,
            content_type=type, object_id=instance.id,
            creator=profile.user, last_modifier=profile.user
        )

        for staff in company_staff:
            bell_status = get_bell_notification_status(
                staff, sender.__base__.__name__.lower()
            )
            email_status = get_email_notification_status(
                staff, sender.__base__.__name__.lower()
            )

            if bell_status or email_status:
                notify_recipient = notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=staff,
                    creator=profile.user, last_modifier=profile.user)
                notify_recipient.save()
                send_push_notification(notify_obj, staff, body)

    except Exception as e:
        print(e)


@receiver([post_save, post_delete], sender=project_models.Team)
def team_notification(sender, instance, **kwargs):
    company_staff = instance.project.profiles.all().union(
        instance.project.company.get_owners_and_delegates()
    )
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        return

    try:
        if 'created' in kwargs:
            if kwargs['created']:
                subject = _('New Staff (%s) added in project (%s)'% (instance.profile.last_name, instance.project.name))
            else:
                subject = _('Staff (%s) updated in project (%s)'% (instance.profile.last_name, instance.project.name))
        else:
            subject = _('Staff (%s) deleted in project (%s)'% (instance.profile.last_name, instance.project.name))

        endpoint = '/apps/projects/{}/team'.format(str(instance.project.id))
        body = json.dumps({
            'content': subject.__str__(),
            'url': endpoint
        })
        type = ContentType.objects.get(model=sender.__name__.lower())

        notify_obj = notify_models.Notify.objects.create(
            sender=profile, subject=subject, body=body,
            content_type=type, object_id=instance.id,
            creator=profile.user, last_modifier=profile.user
        )

        for staff in company_staff:
            bell_status = get_bell_notification_status(
                staff, sender.__name__.lower()
            )
            email_status = get_email_notification_status(
                staff, sender.__name__.lower()
            )

            if bell_status or email_status:
                notify_recipient = notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=staff,
                    creator=profile.user, last_modifier=profile.user)
                notify_recipient.save()
                send_push_notification(notify_obj, staff, body)
    except Exception as e:
        print(e)


@receiver([post_save, post_delete], sender=project_models.Task)
def task_notification(sender, instance, **kwargs):
    try:
        company_staff = instance.project.profiles.all().union(
            instance.project.company.get_owners_and_delegates()
        )
        profile = get_current_profile()
    except:
        return
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        return

    try:
        if instance.assigned_company:
            company_staff = company_staff.union(
                instance.assigned_company.get_owners_and_delegates()
            )

        if instance.shared_task:
            company_staff = company_staff.union(
                instance.shared_task.project.company.get_owners_and_delegates()
            )

        if 'created' in kwargs:
            if kwargs['created']:
                subject = _('New Task (%s) added in project (%s)'% (instance.name, instance.project.name))
            else:
                subject = _('Task (%s) updated in project (%s)'% (instance.name, instance.project.name))
        else:
            subject = _('Task (%s) deleted in project (%s)'% (instance.name, instance.project.name))

        endpoint = '/apps/projects/{}/task'.format(str(instance.project.id))
        body = json.dumps({
            'content': subject.__str__(),
            'url': endpoint
        })
        type = ContentType.objects.get(model=sender.__name__.lower())

        notify_obj = notify_models.Notify.objects.create(
            sender=profile, subject=subject, body=body,
            content_type=type, object_id=instance.id,
            creator=profile.user, last_modifier=profile.user
        )

        for staff in company_staff:
            bell_status = get_bell_notification_status(
                staff, sender.__name__.lower()
            )
            email_status = get_email_notification_status(
                staff, sender.__name__.lower()
            )

            if bell_status or email_status:
                notify_recipient = notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=staff,
                    creator=profile.user, last_modifier=profile.user)
                notify_recipient.save()
                send_push_notification(notify_obj, staff, body)

    except Exception as e:
        print(e)


@receiver([post_save, post_delete], sender=project_models.Activity)
def activity_notification(sender, instance, **kwargs):
    try:
        company_staff = instance.workers.all().union(
            instance.task.project.company.get_owners_and_delegates()
        )
    except:
        return
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        return

    try:
        if 'created' in kwargs:
            if kwargs['created']:
                subject = _('New Activity (%s) added in project (%s)'% (instance.title, instance.task.project.name))
            else:
                subject = _('Activity (%s) updated in project (%s)'% (instance.title, instance.task.project.name))
        else:
            subject = _('Activity (%s) deleted in project (%s)'% (instance.title, instance.task.project.name))

        endpoint = '/apps/projects/{}/task'.format(str(instance.task.project.id))
        body = json.dumps({
            'content': subject.__str__(),
            'url': endpoint
        })
        type = ContentType.objects.get(model=sender.__name__.lower())

        notify_obj = notify_models.Notify.objects.create(
            sender=profile, subject=subject, body=body,
            content_type=type, object_id=instance.id,
            creator=profile.user, last_modifier=profile.user
        )

        for staff in company_staff:
            bell_status = get_bell_notification_status(
                staff, sender.__name__.lower()
            )
            email_status = get_email_notification_status(
                staff, sender.__name__.lower()
            )

            if bell_status or email_status:
                notify_recipient = notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=staff,
                    creator=profile.user, last_modifier=profile.user)
                notify_recipient.save()
                send_push_notification(notify_obj, staff, body)

    except Exception as e:
        print(e)


@receiver([post_save, post_delete], sender=project_models.Post)
def post_notification(sender, instance, **kwargs):
    try:
        if instance.sub_task is not None:
            company_staff = instance.sub_task.workers.all().union(
                instance.sub_task.task.project.company.get_owners_and_delegates()
            )
            post_for_model = 'activity'
        else:
            company_staff = instance.task.project.profiles.all().union(
                instance.task.project.company.get_owners_and_delegates()
            )
            post_for_model = 'task'

    except:
        return
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        return

    try:
        if post_for_model == 'activity':
            if 'created' in kwargs:
                if kwargs['created']:
                    subject = _('New Post added in activity (%s)'% (instance.sub_task.name))
                else:
                    subject = _('Post updated in activity (%s)'% (instance.sub_task.name))
            else:
                subject = _('Post deleted in activity (%s)'% (instance.sub_task.name))
        else:
            if 'created' in kwargs:
                if kwargs['created']:
                    subject = _('New Post added in task (%s)' % (instance.task.name))
                else:
                    subject = _('Post updated in task (%s)' % (instance.task.name))
            else:
                subject = _('Post deleted in task (%s)' % (instance.task.name))
        try:
            endpoint = '/apps/projects/{}/task'.format(str(instance.task.project.id))
        except:
            endpoint = '/apps/projects/{}/task'.format(str(instance.activity.task.project.id))
        body = json.dumps({
            'content': subject.__str__(),
            'url': endpoint
        })
        type = ContentType.objects.get(model=sender.__name__.lower())

        notify_obj = notify_models.Notify.objects.create(
            sender=profile, subject=subject, body=body,
            content_type=type, object_id=instance.id,
            creator=profile.user, last_modifier=profile.user
        )

        for staff in company_staff:
            bell_status = get_bell_notification_status(
                staff, sender.__name__.lower()
            )
            email_status = get_email_notification_status(
                staff, sender.__name__.lower()
            )

            if bell_status or email_status:
                notify_recipient = notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=staff,
                    creator=profile.user, last_modifier=profile.user)
                notify_recipient.save()
                send_push_notification(notify_obj, staff, body)

    except Exception as e:
        print(e)


@receiver([post_save, post_delete], sender=project_models.Comment)
def comment_notification(sender, instance, **kwargs):
    try:
        if instance.post.sub_task is not None:
            company_staff = instance.post.sub_task.workers.all().union(
                instance.post.sub_task.task.project.company.get_owners_and_delegates()
            )
            post_for_model = 'activity'
        else:
            company_staff = instance.post.task.project.profiles.all().union(
                instance.post.task.project.company.get_owners_and_delegates()
            )
            post_for_model = 'task'

    except:
        return
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        return

    try:
        if post_for_model == 'activity':
            if 'created' in kwargs:
                if kwargs['created']:
                    subject = _('New Comment added in post activity (%s)'% (instance.post.sub_task.name))
                else:
                    subject = _('Comment updated in post activity (%s)'% (instance.post.sub_task.name))
            else:
                subject = _('Comment deleted in post activity (%s)'% (instance.post.sub_task.name))
        else:
            if 'created' in kwargs:
                if kwargs['created']:
                    subject = _('New Comment added in post task (%s)' % (instance.post.task.name))
                else:
                    subject = _('Comment updated in post task (%s)' % (instance.post.task.name))
            else:
                subject = _('Comment deleted in post task (%s)' % (instance.post.task.name))
        try:
            endpoint = '/apps/projects/{}/task'.format(str(instance.post.task.project.id))
        except:
            endpoint = '/apps/projects/{}/task'.format(str(instance.post.activity.task.project.id))
        body = json.dumps({
            'content': subject.__str__(),
            'url': endpoint
        })
        type = ContentType.objects.get(model=sender.__name__.lower())

        notify_obj = notify_models.Notify.objects.create(
            sender=profile, subject=subject, body=body,
            content_type=type, object_id=instance.id,
            creator=profile.user, last_modifier=profile.user
        )

        for staff in company_staff:
            bell_status = get_bell_notification_status(
                staff, sender.__name__.lower()
            )
            email_status = get_email_notification_status(
                staff, sender.__name__.lower()
            )

            if bell_status or email_status:
                notify_recipient = notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=staff,
                    creator=profile.user, last_modifier=profile.user)
                notify_recipient.save()
                send_push_notification(notify_obj, staff, body)

    except Exception as e:
        print(e)