# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import warnings
import uuid
from calendar import timegm
from datetime import datetime

from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.compat import get_username
from rest_framework_jwt.compat import get_username_field

jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


def custom_jwt_payload_handler(user, extra_dictionary=None):
    username_field = get_username_field()
    username = get_username(user)

    warnings.warn(
        'The following fields will be removed in the future: '
        '`email` and `user_id`. ',
        DeprecationWarning
    )

    payload = {
        'user_id': user.pk,
        'username': username,
        'extra': extra_dictionary,
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
    }
    if hasattr(user, 'email'):
        payload['email'] = user.email
    if isinstance(user.pk, uuid.UUID):
        payload['user_id'] = str(user.pk)

    payload[username_field] = username

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.WT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload


def custom_jwt_response_payload_handler(token, user=None, request=None):
    payload = jwt_decode_handler(token)
    data = {
        'token': token,
        'user': '{}'.format(user.id),
        'active': user.is_active,
        'extra': payload['extra'],
        'exp': payload['exp'],
        'orig_iat': payload['orig_iat']
    }
    return data
