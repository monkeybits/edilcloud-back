# -*- coding: utf-8 -*-

from django.conf.urls import url

from rest_auth.views import (
    PasswordChangeView, PasswordResetView,
    PasswordResetConfirmView, UserDetailsView
)

from rest_framework_jwt.views import ObtainJSONWebToken, verify_jwt_token

from .views import generic_views
from .views import tracker_views
from .serializers import CustomLoginJWTSerializer
from web.serializers import MyPasswordResetSerializer


user_urlpatterns = [
    url(
        r'^$',
        UserDetailsView.as_view(),
        name='rest_user_details'
    ),
    url(
        r'^password/change/$',
        PasswordChangeView.as_view(),
        name='rest_password_change'
    ),

    url(
        r'^password/reset/confirm/$',
        PasswordResetConfirmView.as_view(),
        name='rest_password_reset_confirm'
    ),
    url(
        r'^token/verify/$',
        verify_jwt_token
    ),
]

generic_urlpatterns = [
    url(
        r'^registration/$',
        generic_views.RegistrationAPIView.as_view(),
        name='rest_registration'
    ),
    url(
        r'^activate/registration/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+?)/$',
        generic_views.ActivateRegistrationAPIView.as_view(),
        name='rest_activate_registration'
    ),
    url(
        r'^login/$',
        ObtainJSONWebToken.as_view(serializer_class=CustomLoginJWTSerializer)
    ),
    url(
        r'^password/reset/$',
        PasswordResetView.as_view(serializer_class=MyPasswordResetSerializer),
        name='rest_password_reset'
    ),
]

tracker_urlpatterns = [
    url(
        r'^token/refresh/(?P<profile_pk>\d+)/$',
        tracker_views.TokenRefreshAPIView.as_view(),
        name='rest_token_refresh'
    ),
]

urlpatterns = user_urlpatterns + generic_urlpatterns + tracker_urlpatterns
