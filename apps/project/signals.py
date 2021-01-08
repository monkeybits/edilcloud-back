import json
import logging

import emoji
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from web.utils import build_array_message
from . import models as project_models
from apps.notify import models as notify_models
from web.core.middleware.thread_local import get_current_profile
from web.core.utils import get_bell_notification_status, get_email_notification_status
from ..notify.signals import send_push_notification

# @receiver([post_save, post_delete], sender=project_models.Project)
# def project_notification(sender, instance, **kwargs):
#     company_staff = instance.profiles.all().union(
#         instance.company.get_owners_and_delegates()
#     )
#     profile = get_current_profile()
#     # If there is no JWT token in the request,
#     # then we don't create notifications (Useful at admin & shell for debugging)
#     if not profile:
#         return
#
#     try:
#         endpoint = '/apps/projects/{}'.format(str(instance.id))
#         if 'created' in kwargs:
#             if kwargs['created']:
#                 subject = _('New Project (%s) created in company (%s)'% (instance.name, instance.company.name))
#             else:
#                 subject = _('Project (%s) updated in company (%s)'% (instance.name, instance.company.name))
#         else:
#             subject = _('Project (%s) deleted in company (%s)'% (instance.name, instance.company.name))
#
#         body = json.dumps({
#             'content': subject.__str__(),
#             'url': endpoint
#         })
#         type = ContentType.objects.get(model=sender.__name__.lower())
#
#         notify_obj = notify_models.Notify.objects.create(
#             sender=profile, subject=subject, body=body,
#             content_type=type, object_id=instance.id,
#             creator=profile.user, last_modifier=profile.user
#         )
#
#         for staff in company_staff:
#             bell_status = get_bell_notification_status(
#                 staff, sender.__base__.__name__.lower()
#             )
#             email_status = get_email_notification_status(
#                 staff, sender.__base__.__name__.lower()
#             )
#
#             if bell_status or email_status:
#                 notify_recipient = notify_models.NotificationRecipient(
#                     notification=notify_obj, is_email=email_status,
#                     is_notify=bell_status, recipient=staff,
#                     creator=profile.user, last_modifier=profile.user)
#                 notify_recipient.save()
#                 send_push_notification(notify_obj, staff, body)
#
#     except Exception as e:
#         print(e)

def team_invite_notification(sender, instance, **kwargs):
    company_staff = instance.project.profiles.all().union(
        instance.project.company.get_owners_and_delegates()
    )
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        return

    try:
        subject = build_array_message('house', [
            _('You have been invited in a project')
        ])
        endpoint = '/apps/projects'.format(str(instance.project.id))
        body = json.dumps({
            'content': build_array_message(None, [
                _('You have been invited in project'),
                instance.project.name,
                _('from company'),
                instance.project.company.name
            ]),
            'url': endpoint,
            'project_id': instance.project.id
        })
        type = ContentType.objects.get(model=sender.__name__.lower())

        notify_obj = notify_models.Notify.objects.create(
            sender=profile, subject=subject, body=body,
            content_type=type, object_id=instance.id,
            creator=profile.user, last_modifier=profile.user
        )

        bell_status = get_bell_notification_status(
            instance.profile, sender.__name__.lower()
        )
        email_status = get_email_notification_status(
            instance.profile, sender.__name__.lower()
        )
        translation.activate(profile.user.get_main_profile().language)
        if bell_status or email_status:
            notify_recipient = notify_models.NotificationRecipient(
                notification=notify_obj, is_email=email_status,
                is_notify=bell_status, recipient=instance.profile,
                creator=profile.user, last_modifier=profile.user)
            notify_recipient.save()
            send_push_notification(notify_obj, instance.profile, subject, body)
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
                subject = build_array_message('construction_worker', [
                    _('You have been added in a project')
                ])
                content = build_array_message(None, [
                    _('You have been added in project'),
                    instance.project.name
                ])
            else:
                return
        else:
            subject = build_array_message('do_not_litter', [
                _('You have been deleted from project')
            ])
            content = build_array_message(None, [
                _('User'),
                "{} {}".format(profile.first_name, profile.last_name),
                _('has removed you from project'),
                instance.project.name
            ])

        endpoint = '/apps/projects/{}/team'.format(str(instance.project.id))
        body = json.dumps({
            'content': content,
            'url': endpoint,
            'project_id': instance.project.id
        })
        type = ContentType.objects.get(model=sender.__name__.lower())

        notify_obj = notify_models.Notify.objects.create(
            sender=profile, subject=subject, body=body,
            content_type=type, object_id=instance.id,
            creator=profile.user, last_modifier=profile.user
        )

        for staff in company_staff:
            if 'created' in kwargs:
                if kwargs['created']:
                    if instance.profile.id == staff.id:
                        continue
            bell_status = get_bell_notification_status(
                staff, sender.__name__.lower()
            )
            email_status = get_email_notification_status(
                staff, sender.__name__.lower()
            )
            translation.activate(staff.user.get_main_profile().language)
            if bell_status or email_status:
                notify_recipient = notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=staff,
                    creator=profile.user, last_modifier=profile.user)
                notify_recipient.save()
                send_push_notification(notify_obj, staff, subject, body)
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
                subject = build_array_message('clipboard', [
                    _('New assignment for your company')
                ])
            else:
                subject = _('Task (%s) updated in project (%s)'% (instance.name, instance.project.name))
                return
        else:
            subject = _('Task (%s) deleted in project (%s)'% (instance.name, instance.project.name))
            return

        endpoint = '/apps/projects/{}/task'.format(str(instance.project.id))
        body = json.dumps({
            'content': build_array_message(None, [
                _('Company'),
                instance.project.company.name,
                _('has assigned you task'),
                instance.name,
                _('in project'),
                instance.project.name
            ]),
            'url': endpoint,
            'project_id': instance.project.id
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
            translation.activate(staff.user.get_main_profile().language)
            if bell_status or email_status:
                notify_recipient = notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=staff,
                    creator=profile.user, last_modifier=profile.user)
                notify_recipient.save()
                send_push_notification(notify_obj, staff, subject, body)

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
                subject = build_array_message('heavy_plus_sign', [
                    _('New activity assigned')
                ])
            else:
                subject = _('Activity').__str__ () + " %s " % instance.title + _("updated in project").__str__() + " %s" % instance.task.project.name
                return
        else:
            subject = _('Activity').__str__ () + " %s " % instance.title + _("deleted in project").__str__() + " %s" % instance.task.project.name
            return

        endpoint = '/apps/projects/{}/task'.format(str(instance.task.project.id))
        body = json.dumps({
            'content': build_array_message(None, [
                _('Person'),
                "{} {}".format(profile.first_name, profile.last_name),
                _('has assigned you activity'),
                instance.title,
                _('in project'),
                instance.task.project.name
            ]),
            'url': endpoint,
            'task_id': instance.task.id,
            'project_id': instance.task.project.id
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
            translation.activate(staff.user.get_main_profile().language)
            if bell_status or email_status:
                notify_recipient = notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=staff,
                    creator=profile.user, last_modifier=profile.user)
                notify_recipient.save()
                send_push_notification(notify_obj, staff, subject, body)

    except Exception as e:
        print(e)

def alert_notification(sender, instance, **kwargs):
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
            if instance.alert:
                subject = build_array_message('warning',[
                    _('There is an issue in an activity')
                ])
                content = build_array_message(None, [
                    _('User'),
                    "{} {}".format(profile.first_name, profile.last_name),
                    _('has reported an issue in activity'),
                    instance.sub_task.title,
                    _('of project'),
                    instance.sub_task.task.project.name
                ])
            else:
                subject = build_array_message('warning', [
                    _('Issue resolved in an activity')
                ])
                content = build_array_message(None, [
                    _('User'),
                    "{} {}".format(profile.first_name, profile.last_name),
                    _('has resolved an issue in activity'),
                    instance.sub_task.title,
                    _('of project'),
                    instance.sub_task.task.project.name
                ])
        else:
            if instance.alert:
                subject = build_array_message('warning', [
                    _('There is an issue in a task')
                ])
                content = build_array_message(None, [
                    _('User'),
                    "{} {}".format(profile.first_name, profile.last_name),
                    _('has reported an issue in task'),
                    instance.task.name,
                    _('of project'),
                    instance.task.project.name
                ])
            else:
                subject = build_array_message('warning', [
                    _('Issue resolved in a task')
                ])
                content = build_array_message(None, [
                    _('User'),
                    "{} {}".format(profile.first_name, profile.last_name),
                    _('has resolved an issue in task'),
                    instance.task.name,
                    _('of project'),
                    instance.task.project.name
                ])

        try:
            endpoint = '/apps/projects/{}/task'.format(str(instance.task.project.id))
        except:
            endpoint = '/apps/projects/{}/task'.format(str(instance.sub_task.task.project.id))
        if instance.sub_task is not None:
            body = json.dumps({
                'content': content,
                'url': endpoint,
                'activity_id': instance.sub_task.id,
                'task_id': instance.sub_task.task.id,
                'project_id': instance.sub_task.task.project.id
            })
        else:
            body = json.dumps({
                'content': content,
                'url': endpoint,
                'task_id': instance.task.id,
                'project_id': instance.task.project.id
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
            translation.activate(staff.user.get_main_profile().language)
            if bell_status or email_status:
                notify_recipient = notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=staff,
                    creator=profile.user, last_modifier=profile.user)
                notify_recipient.save()
                if post_for_model == 'task':
                    send_push_notification(notify_obj, staff, subject, body)
                else:
                    send_push_notification(notify_obj, staff, subject, body)
    except Exception as e:
        print(e)


#@receiver([post_save, post_delete], sender=project_models.Post)
def post_notification(sender, instance, kwargs=None):
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
                    subject = build_array_message('mailbox_with_mail', [
                        _('New post has been created')
                    ])
                    content = build_array_message(None, [
                        _('User'),
                        "{} {}".format(profile.first_name, profile.last_name),
                        _('has created a new post in activity'),
                        instance.sub_task.title
                    ])
                else:
                    subject = '%s ' % emoji.emojize(':pencil:') + _("Post updated in activity").__str__() + " %s" + instance.sub_task.title
                    return
            else:
                subject = '%s ' % emoji.emojize(':pencil:') + _("Post deleted in activity").__str__() + " %s" + instance.sub_task.title
                return
        else:
            if 'created' in kwargs:
                if kwargs['created']:
                    subject = build_array_message('mailbox_with_mail', [
                        _('New post has been created')
                    ])
                    content = build_array_message(None, [
                        _('User'),
                        "{} {}".format(profile.first_name, profile.last_name),
                        _('has created a new post in task'),
                        instance.task.name
                    ])
                else:
                    subject = '%s ' % emoji.emojize(':pencil:') + _("Post updated in task").__str__ () + " %s" + instance.task.name
                    return
            else:
                subject = '%s ' % emoji.emojize(':pencil:') + _("Post deleted in task").__str__() + " %s" + instance.task.name
                return
        try:
            endpoint = '/apps/projects/{}/task'.format(str(instance.task.project.id))
        except:
            endpoint = '/apps/projects/{}/task'.format(str(instance.sub_task.task.project.id))
        if instance.sub_task is not None:
            body = json.dumps({
                'content': content,
                'url': endpoint,
                'activity_id': instance.sub_task.id,
                'task_id': instance.sub_task.task.id,
                'project_id': instance.sub_task.task.project.id
            })
        else:
            body = json.dumps({
                'content': content,
                'url': endpoint,
                'task_id': instance.task.id,
                'project_id': instance.task.project.id
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
            translation.activate(staff.user.get_main_profile().language)
            if bell_status or email_status:
                notify_recipient = notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=staff,
                    creator=profile.user, last_modifier=profile.user)
                notify_recipient.save()
                if post_for_model == 'task':
                    send_push_notification(notify_obj, staff, subject, body)
                else:
                    send_push_notification(notify_obj, staff, subject, body)
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

    except Exception as e:
        logging.error(e.__str__())
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile:
        return

    try:
        if post_for_model == 'activity':
            if 'created' in kwargs:
                if kwargs['created']:
                    subject = build_array_message('speech_balloon', [
                        _('There is a new comment')
                    ])
                    content = build_array_message(None, [
                        _('User'),
                        "{} {}".format(profile.first_name, profile.last_name),
                        _('has commented post'),
                        instance.post.text[:50] + '..',
                        _('in activity'),
                        instance.post.sub_task.title
                    ])
                else:
                    subject = '%s ' % emoji.emojize(':speech_balloon:') + _("Comment updated in post activity").__str__() + " (%s)" % instance.post.sub_task.title
                    return
            else:
                subject = '%s ' % emoji.emojize(':speech_balloon:') + _("Comment deleted in post activity").__str__() + " (%s)" % instance.post.sub_task.title
                return
        else:
            if 'created' in kwargs:
                if kwargs['created']:
                    subject = build_array_message('speech_balloon', [
                        _('There is a new comment')
                    ])
                    content = build_array_message(None, [
                        _('User'),
                        "{} {}".format(profile.first_name, profile.last_name),
                        _('has commented post'),
                        instance.post.text[:50] + '..',
                        _('in task'),
                        instance.post.task.name
                    ])
                else:
                    subject = "%s " % emoji.emojize(':speech_balloon:') + _('Comment updated in post task').__str__() + " (%s)" % instance.post.task.name
                    return
            else:
                subject = "%s " % emoji.emojize(':speech_balloon:') + _('Comment deleted in post task').__str__() + " (%s)" % instance.post.task.name
                return
        print(subject)
        try:
            print('endpoint comment for task')
            endpoint = '/apps/projects/{}/task'.format(str(instance.post.task.project.id))
        except:
            print('endpoint comment for subtask')
            print(instance.post.sub_task.task)
            endpoint = '/apps/projects/{}/task'.format(str(instance.post.sub_task.task.project.id))
            print('---------------------------------')


        if instance.parent:
            body = {
                'content': content,
                'url': endpoint,
                'comment_id': instance.parent.id,
            }
        else:
            body = {
                'content': content,
                'url': endpoint,
            }
        if instance.post.task:
            body['task_id'] = instance.post.task.id
            body['project_id'] = instance.post.task.project.id
        else:
            body['task_id'] = instance.post.sub_task.task.id
            body['activity_id'] = instance.post.sub_task.id
            body['project_id'] = instance.post.sub_task.task.project.id

        body = json.dumps(body)
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
            translation.activate(staff.user.get_main_profile().language)
            if bell_status or email_status:
                notify_recipient = notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=staff,
                    creator=profile.user, last_modifier=profile.user)
                notify_recipient.save()
                if post_for_model == 'task':
                    send_push_notification(notify_obj, staff, subject, body)
                else:
                    send_push_notification(notify_obj, staff, subject, body)
    except Exception as e:
        logging.error(e.__str__())