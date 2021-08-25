# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from datetime import datetime

import jwt

from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import status, permissions
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import JSONWebTokenAPIView

from ..serializers import RegisterSerializer
from .mixin import UserMixin, TokenGenerator

User = get_user_model()
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class RegistrationAPIView(
        generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True
        first_name = request.data.pop('first_name')
        last_name = request.data.pop('last_name')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        main_profile = user.create_main_profile({
            'first_name': first_name,
            'last_name': last_name,
            'language': 'it'
        })
        headers = self.get_success_headers(serializer.data)
        user.send_account_verification_email()
        from web.tasks import update_gspread_users
        if os.environ.get('ENV_NAME') == 'test':
            update_gspread_users.delay(
                {
                    'email': user.email,
                    'first_name': main_profile.first_name,
                    'last_name': main_profile.last_name,
                    'role': main_profile.role,
                    'company': main_profile.company.name if hasattr(main_profile, 'company') else '',
                    'subscription_date': datetime.utcnow(),
                    'phone': main_profile.phone
                }
            )
        return Response(
            {
                'detail': 'Registration Successful'
            },
            status=status.HTTP_201_CREATED, headers=headers
        )


class ActivateRegistrationAPIView(
        UserMixin,
        generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def set_active(self, user):
        if not user.is_active:
            user.is_active = True
            user.save()
            return True
        return False

    def get(self, request, *args, **kwargs):
        token = kwargs.pop('token')
        uidb64 = kwargs.pop('uidb64')
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            msg = _('Activation Link not found.')
            raise exceptions.AuthenticationFailed(msg)
        account_activation_token = TokenGenerator()
        if user is not None and account_activation_token.check_token(user, token):
            active_status = self.set_active(user)
        else:
            msg = _('Activation Link expired')
            raise exceptions.AuthenticationFailed(msg)

        return Response(
            {
                'detail': 'User Activated' if active_status else 'User is already activated'
            },
            status=status.HTTP_200_OK
        )


class CustomJSONWebTokenAPIView(JSONWebTokenAPIView):

    def post(self, request, *args, **kwargs):
        from apps.profile.models import Profile
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            profiles = Profile.objects.filter(user=user)
            for main_profile in profiles:
                if main_profile.is_main:
                    response_data['main_profile'] = main_profile.pk
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
