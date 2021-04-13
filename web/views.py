import os
import shutil
from io import BytesIO
from os.path import splitext, basename
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import urlopen
from django.utils.translation import ugettext_lazy as _
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.providers.linkedin_oauth2.views import LinkedInOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from django.core.files import File
from rest_framework import status, permissions, generics, serializers

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_auth.models import TokenModel

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from social_core.backends.oauth import BaseOAuth2
from social_core.exceptions import AuthForbidden, AuthTokenError, MissingBackend
from social_django.utils import load_backend, load_strategy

from apps.user.api.frontend.serializers import jwt_encode_handler, jwt_payload_handler, User
from apps.user.views import custom_jwt_response_payload_handler

def common_operations(self, request, custom_function):
    serializer = self.serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)
    provider = serializer.data.get('provider', None)
    strategy = load_strategy(request)
    try:
        backend = load_backend(strategy=strategy, name=provider,
                               redirect_uri=None)

    except MissingBackend:
        return Response({'error': _('Please provide a valid provider')},
                        status=status.HTTP_400_BAD_REQUEST)
    response = custom_function(backend, serializer)
    if type(response) is dict:
        user = response['user']
        access_token = response['access_token']
    else:
        return response, None, serializer, provider
    try:
        authenticated_user = backend.do_auth(access_token, user=user)
    except HTTPError as error:
        return Response({
            "error": "invalid token",
            "details": str(error)
        }, status=status.HTTP_400_BAD_REQUEST)

    except AuthForbidden as error:
        return Response({
            "error": "invalid token",
            "details": str(error)
        }, status=status.HTTP_400_BAD_REQUEST)

    if authenticated_user:
        # generate JWT token
        # login(request, authenticated_user)
        data = {
            "token": jwt_encode_handler(
                jwt_payload_handler(user)
            )}
        # customize the response to your needs
        response = custom_jwt_response_payload_handler(data.get('token'), authenticated_user)
        return response, authenticated_user, serializer, provider
    else:
        print('error login: not authenticated')
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'error': _('Unable to log in with provided credentials.')})


class SocialAuthSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=255, required=True)
    access_token = serializers.CharField(max_length=4096, required=True, trim_whitespace=True)
    photo = serializers.URLField(max_length=1000, allow_blank=True, allow_null=False)

class SocialRegisterView(generics.GenericAPIView):
    serializer_class = SocialAuthSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Authenticate user through the provider and access_token"""
        def custom_function(backend, serializer):
            try:
                if isinstance(backend, BaseOAuth2):
                    access_token = serializer.data.get('access_token')
                user_data = backend.user_data(access_token)
                if 'email' in user_data:
                    if User.objects.filter(email=user_data['email']):
                        return Response({
                            "error": _("Already exists an account with this email")
                        }, status=status.HTTP_400_BAD_REQUEST)
                user = backend.do_auth(access_token)
            except HTTPError as error:
                return Response({
                    "error": {
                        "access_token": _("Invalid token"),
                        "details": str(error)
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            except AuthTokenError as error:
                return Response({
                    "error": _("Invalid credentials"),
                    "details": str(error)
                }, status=status.HTTP_400_BAD_REQUEST)
            return {'user': user, 'access_token': access_token}


        response, authenticated_user, serializer, provider = common_operations(self, request, custom_function)
        try:
            main_profile = authenticated_user.create_main_profile({
                'first_name': authenticated_user.first_name,
                'last_name': authenticated_user.last_name,
                'language': 'it'
            })
            # url, filename, model_instance assumed to be provided
            res = urlopen(serializer.data['photo'])
            io = BytesIO(res.read())
            disassembled = urlparse(serializer.data['photo'])
            filename, file_ext = splitext(basename(disassembled.path))
            main_profile.photo.save(
                "{}_{}_{}{}".format(provider, authenticated_user.first_name, authenticated_user.last_name, file_ext),
                File(io))
            authenticated_user.is_active = False
            authenticated_user.save()
            authenticated_user.send_account_verification_email()
            from web.tasks import update_gspread_users
            if os.environ.get('ENV_NAME') == 'test':
                update_gspread_users.delay(
                    {
                        'email': authenticated_user.email,
                        'full_name': "{} {}".format(main_profile.first_name, main_profile.last_name),
                        'role': main_profile.role
                    }
                )
            return Response(status=status.HTTP_201_CREATED, data={'detail': _('Registration successful')})
        except Exception as e:
            print(e.__str__())
            return response


class SocialLoginView(generics.GenericAPIView):
    serializer_class = SocialAuthSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Authenticate user through the provider and access_token"""

        def custom_function(backend, serializer):
            try:
                if isinstance(backend, BaseOAuth2):
                    access_token = serializer.data.get('access_token')
                user_data = backend.user_data(access_token)
                if 'email' in user_data:
                    if not User.objects.filter(email=user_data['email']):
                        return Response(status=status.HTTP_400_BAD_REQUEST,
                                        data={'error': _('Unable to log in with provided credentials.') + 'non sei utente del sistema'})
                user = backend.do_auth(access_token)
            except HTTPError as error:
                return Response({
                    "error": {
                        "access_token": _("Invalid token"),
                        "details": str(error)
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            except AuthTokenError as error:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'error': _('Unable to log in with provided credentials.') + ' token invalido'})
            return {'user': user, 'access_token': access_token}

        response, authenticated_user, serializer, provider = common_operations(self, request, custom_function)

        try:
            if not authenticated_user.is_active:
                authenticated_user.send_account_verification_email()
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'error': _('Your account is disabled, check your email to activate it')})
            main_profile = authenticated_user.get_main_profile()
            # url, filename, model_instance assumed to be provided
            res = urlopen(serializer.data['photo'])
            io = BytesIO(res.read())
            disassembled = urlparse(serializer.data['photo'])
            filename, file_ext = splitext(basename(disassembled.path))
            # try:
            #     shutil.rmtree(main_profile.photo.path.rsplit('/', 1)[0])
            # except Exception as es:
            #     print(es.__str__())
            # main_profile.photo.save(
            #     "{}_{}_{}{}".format(provider, authenticated_user.first_name, authenticated_user.last_name, file_ext),
            #     File(io))
        except Exception as e:
            print(e.__str__())
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'error': _('Unable to log in with provided credentials.') + 'main profile error'})

        return Response(status=status.HTTP_200_OK, data=response)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class FacebookRegister(SocialRegisterView):
    adapter_class = FacebookOAuth2Adapter


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class GoogleRegister(SocialRegisterView):
    adapter_class = GoogleOAuth2Adapter