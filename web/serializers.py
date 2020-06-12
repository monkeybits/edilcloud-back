# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.contrib.auth.forms import PasswordResetForm

from rest_auth import serializers as rest_auth_serializers


class MyPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        email_message.content_subtype = 'html'
        email_message.send()


class MyDefaultPasswordResetSerializer(rest_auth_serializers.PasswordResetSerializer):
    password_reset_form_class = MyPasswordResetForm

    def get_email_options(self):
        return {"extra_email_context": {"base_url": settings.BASE_URL}}


class MyPasswordResetSerializer(MyDefaultPasswordResetSerializer):
    pass
