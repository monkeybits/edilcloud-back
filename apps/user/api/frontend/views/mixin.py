# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

from rest_framework_jwt.settings import api_settings

jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


class UserMixin(object):
    def get_jwt_payload_handler(self, user):
        return jwt_payload_handler(user)

    def get_jwt_encode_handler(self, payload):
        return jwt_encode_handler(payload)

    def get_jwt_decode_handler(self, token):
        return jwt_decode_handler(token)


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
