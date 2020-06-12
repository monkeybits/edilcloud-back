# -*- coding: utf-8 -*-

from django.conf import settings
from django.template.loader import render_to_string


def get_setting(setting_name, default):
    return getattr(settings, setting_name, default)


def get_bell_notification_status(profile, event):
    try:
        bell_notify = profile.preference.notification['bell']
        if bell_notify['status']:
            event = [d for d in bell_notify['typology'] if d['name'] == event][0]
            if event['status']:
                return True
        return False
    except:
        return True


def get_email_notification_status(profile, event):
    try:
        email_notify = profile.preference.notification['email']
        if email_notify['status']:
            event = [d for d in email_notify['typology'] if d['name'] == event][0]
            if event['status']:
                return True
        return False
    except:
        return True


def get_html_message(content, final_content, endpoint=None):
    context = {
        "content": content,
        "final_content": final_content,
        "endpoint": endpoint,
    }

    if endpoint:
        # Html message
        html_message = render_to_string('notify/notify/bell/notify.html', context)
    else:
        html_message = render_to_string('notify/notify/bell/notify_no_button.html', context)
    return html_message
