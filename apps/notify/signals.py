import json

from asgiref.sync import async_to_sync
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from . import models as notify_models
from channels.layers import get_channel_layer

def event_triger(msg):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'notify_notify_channel',
        {
            'type': 'notify_message',
            'message': msg
        }
    )

@receiver([post_save, post_delete], sender=notify_models.NotificationRecipient)
def notify_notification(sender, instance, **kwargs):
    notify_obj = instance.notification
    recipient = instance
    event_triger({
        "message": {
            "id": notify_obj.id,
            "content_type": notify_obj.content_type.name,
            "body": json.loads(notify_obj.body),
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