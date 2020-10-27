# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework_jwt.views import JSONWebTokenAPIView

from .generic_views import CustomJSONWebTokenAPIView
from .. import serializers


class TokenRefreshAPIView(
        CustomJSONWebTokenAPIView):
    serializer_class = serializers.TokenRefreshAPISerializer

    def get_serializer_context(self):
        profile_id = self.kwargs.get('profile_pk', None)
        return {
            'request': self.request,
            'profile_id': profile_id
        }
