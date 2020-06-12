# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import jwt

from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import status, permissions
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import exceptions

from ..serializers import RegisterSerializer
from .mixin import UserMixin, TokenGenerator

User = get_user_model()


class RegistrationAPIView(
        generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        user.send_account_verification_email()
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
