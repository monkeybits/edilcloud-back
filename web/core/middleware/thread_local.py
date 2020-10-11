# -*- coding: utf-8 -*-

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local


import logging

from web.api.views import jwt_decode_handler

logger = logging.getLogger('thread_local')

_thread_locals = local()


def get_current_request():
    return getattr(_thread_locals, 'request', None)


def get_profile_payload():
    request = get_current_request()
    token = request.META['HTTP_AUTHORIZATION'].split()[1]
    payload = jwt_decode_handler(token)
    return payload['extra']['profile']


def get_current_profile():
    try:
        from apps.profile import models as profile_models
        profile_payload = get_profile_payload()
        profile = profile_models.Profile.objects.get(pk=profile_payload['id'])
        return profile
    except:
        return None


def get_current_user():
    request = get_current_request()
    if request:
        return getattr(request, 'user', None)


class ThreadLocalMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        return self.get_response(request)
