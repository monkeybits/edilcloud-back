import json

import emoji
import requests
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from . import models as notify_models
from channels.layers import get_channel_layer
import firebase_admin
from firebase_admin import credentials, messaging
from ..project.models import Project
import datetime

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred)

def event_triger(msg):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'notify_notify_channel',
        {
            'type': 'notify_message',
            'message': msg
        }
    )


def addRedirectUrl(talk):
    if talk.content_type.name == 'company':
        return "https://dev.edilcloud.io/apps/chat"
    if talk.content_type.name == 'project':
        return "https://dev.edilcloud.io/apps/projects/{}".format(str(talk.object_id))
    return "https://dev.edilcloud.io"


def addHeading(talk, notify_obj):
    if talk.content_type.name == 'company':
        return "{} Company Chat".format(notify_obj.sender.company.name)
    if talk.content_type.name == 'project':
        pr = Project.objects.filter(id=talk.object_id)
        if pr:
            return "{} Project Chat".format(pr[0].name)
        else:
            return "Project Chat"


def send_push_notification(notify_obj, recipient, subject, body):
    body = json.loads(body)
    print(body['content'])
    #
    # payload = {
    #     "app_id": "0fbdf0cf-d9f5-4363-809f-4735b1bba268",
    #     "include_player_ids": list_players_recipients,
    #     "android_group": "project_" + str(body['project_id']),
    #     "contents": {
    #         "en": body['content']
    #     },
    #     "content-available": 1,
    #     "headings": {
    #         "en": subject
    #     },
    #     "big_picture": body['big_picture'] if 'big_picture' in body else None,
    #     "android_channel_id": "4b0b1a93-ec1c-4381-b928-713507c635fe",
    #     "wp_wns_sound": "message",
    #     "android_sound": "message",
    #     "data": {
    #         "custom_data": body['content'],
    #         "redirect_url": "https://test.edilcloud.io" + body['url']
    #     },
    #     "small_icon": "ic_stat_onesignal_default"
    # }
    # The topic name can be optionally prefixed with "/topics/".
    topic = 'user{}'.format(recipient.id)
    print('to topic: {}'.format(topic))
    print('name: {}, surname: {} from company: {}'.format(recipient.first_name, recipient.last_name, recipient.company.name))

    # See documentation on defining a message payload.
    message = messaging.Message(
        notification=messaging.Notification(
            title=subject,
            body=body['content'],
            image=body['big_picture'] if 'big_picture' in body else None,
        ),
        android=messaging.AndroidConfig(
            ttl=datetime.timedelta(seconds=3600),
            priority='high',
            notification=messaging.AndroidNotification(
                icon='ic_stat_onesignal_default',
                color='#f45342',
                visibility='public',
                priority='high'
            ),
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    content_available='1',
                    custom_data={
                        "custom_data": body['content'],
                        "redirect_url": "https://test.edilcloud.io" + body['url']
                    }
                )
            ),
        ),
        data={
            "custom_data": body['content'],
            "redirect_url": "https://app.edilcloud.io" + body['url']
        },
        topic=topic,
    )


    # Send a message to the devices subscribed to the provided topic.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)


@receiver([post_save, post_delete], sender=notify_models.NotificationRecipient)
def notify_notification(sender, instance, **kwargs):
    notify_obj = instance.notification
    recipient = instance
    try:
        body = json.loads(notify_obj.body)
    except Exception as e:
        body = {}
    if recipient.reading_date is None:
        event_triger({
            "message": {
                "id": instance.id,
                "notification_id": notify_obj.id,
                "content_type": notify_obj.content_type.name,
                "object_id": notify_obj.object_id,
                "body": body,
                "dest": {
                    "id": recipient.recipient.pk
                },
                "sender": {
                    "id": notify_obj.sender.id,
                    "first_name": notify_obj.sender.first_name,
                    "last_name": notify_obj.sender.last_name,
                    "photo": None,
                    "role": notify_obj.sender.role,
                    "company": {
                        "id": notify_obj.sender.company.id,
                        "name": notify_obj.sender.company.name,
                        "category": {}
                    }
                },
                "subject": notify_obj.subject
            }
        })
