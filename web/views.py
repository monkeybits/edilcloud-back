import os
import shutil
from io import BytesIO
from os.path import splitext, basename
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import urlopen

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

from apps.user.api.frontend.serializers import jwt_encode_handler, jwt_payload_handler
from apps.user.views import custom_jwt_response_payload_handler


class SocialAuthSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=255, required=True)
    access_token = serializers.CharField(max_length=4096, required=True, trim_whitespace=True)
    photo = serializers.URLField(max_length=255, allow_blank=True, allow_null=False)

class SocialLoginView(generics.GenericAPIView):
    serializer_class = SocialAuthSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Authenticate user through the provider and access_token"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = serializer.data.get('provider', None)
        strategy = load_strategy(request)

        try:
            backend = load_backend(strategy=strategy, name=provider,
                                   redirect_uri=None)

        except MissingBackend:
            return Response({'error': 'Please provide a valid provider'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            if isinstance(backend, BaseOAuth2):
                access_token = serializer.data.get('access_token')
            user = backend.do_auth(access_token)
        except HTTPError as error:
            return Response({
                "error": {
                    "access_token": "Invalid token",
                    "details": str(error)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        except AuthTokenError as error:
            return Response({
                "error": "Invalid credentials",
                "details": str(error)
            }, status=status.HTTP_400_BAD_REQUEST)

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

        if authenticated_user and authenticated_user.is_active:
            # generate JWT token
            # login(request, authenticated_user)
            data = {
                "token": jwt_encode_handler(
                    jwt_payload_handler(user)
                )}
            # customize the response to your needs
            response = custom_jwt_response_payload_handler(data.get('token'), authenticated_user)
            try:
                main_profile = authenticated_user.get_main_profile()
                # url, filename, model_instance assumed to be provided
                response = urlopen(serializer.data['photo'])
                io = BytesIO(response.read())
                disassembled = urlparse(serializer.data['photo'])
                filename, file_ext = splitext(basename(disassembled.path))
                try:
                    shutil.rmtree(main_profile.photo.path.rsplit('/', 1)[0])
                except:
                    pass
                main_profile.photo.save("{}_{}_{}{}".format(provider, authenticated_user.first_name, authenticated_user.last_name, file_ext), File(io))
            except:
                main_profile = authenticated_user.create_main_profile({
                    'first_name': authenticated_user.first_name,
                    'last_name': authenticated_user.last_name,
                    'language': 'it'
                })
                # url, filename, model_instance assumed to be provided
                response = urlopen(serializer.data['photo'])
                io = BytesIO(response.read())
                disassembled = urlparse(serializer.data['photo'])
                filename, file_ext = splitext(basename(disassembled.path))
                main_profile.photo.save("{}_{}_{}{}".format(provider, authenticated_user.first_name, authenticated_user.last_name, file_ext), File(io))

        return Response(status=status.HTTP_200_OK, data=response)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

class PublicAuthentication(SessionAuthentication):
    """
        Set Authentication as public so that everyone can authenticate
    """
    def authenticate(self, request):
        return None


class RestFacebookLoginView(APIView):
    """
        Login or register a user based on an authentication token coming
        from Facebook.
        Returns user data including session id.
    """
    permission_classes = (AllowAny,)
    authentication_classes = (PublicAuthentication,)

    def dispatch(self, *args, **kwargs):
        return super(RestFacebookLoginView, self).dispatch(*args, **kwargs)

    def post(self, request, format=None):
        
        try:
            app = SocialApp.objects.get(provider="facebook")
            adapter = FacebookOAuth2Adapter(request)
            callback_url = 'http://localhost:3000/'
            provider = adapter.get_provider()
            scope = provider.get_scope(request)
            client = OAuth2Client(self.request, app.client_id, app.secret,
                              adapter.access_token_method,
                              adapter.access_token_url,
                              callback_url,
                              scope,
                              scope_delimiter=adapter.scope_delimiter,
                              headers=adapter.headers,
                              basic_auth=adapter.basic_auth)
            data = self.request.data
            code = data.get('code', '')
            access_token = client.get_access_token(code)
            token = adapter.parse_token(access_token)
            token.app = app
            login = adapter.complete_login(request,
                                                app,
                                                token,
                                                response=access_token)
            login.token = token
            complete_social_login(request, login)
            logged_in_user = login.account.user
            token, created= TokenModel.objects.get_or_create(user=logged_in_user)
            return Response({"success" : True, 'key' : token.key})
        except Exception as e:
            # FIXME: Catch only what is needed
            print(e)
            return Response({ "erorr" : True })


class RestGoogleLoginView(APIView):
    """
        Login or register a user based on an authentication token coming
        from Google.
        Returns user data including session id.
    """
    permission_classes = (AllowAny,)
    authentication_classes = (PublicAuthentication,)

    def dispatch(self, *args, **kwargs):
        return super(RestGoogleLoginView, self).dispatch(*args, **kwargs)

    def post(self, request, format=None):
        
        try:
            app = SocialApp.objects.get(provider="google")
            adapter = GoogleOAuth2Adapter(request)
            callback_url = 'http://localhost:3000'
            provider = adapter.get_provider()
            scope = provider.get_scope(request)
            client = OAuth2Client(self.request, app.client_id, app.secret,
                              adapter.access_token_method,
                              adapter.access_token_url,
                              callback_url,
                              scope,
                              scope_delimiter=adapter.scope_delimiter,
                              headers=adapter.headers,
                              basic_auth=adapter.basic_auth)
            data = self.request.data
            code = data.get('code', '')
            access_token = client.get_access_token(code)
            token = adapter.parse_token(access_token)
            token.app = app
            login = adapter.complete_login(request,
                                                app,
                                                token,
                                                response=access_token)
            login.token = token
            complete_social_login(request, login)
            logged_in_user = login.account.user
            token, created= TokenModel.objects.get_or_create(user=logged_in_user)
            return Response({"success" : True, 'key' : token.key})
        except Exception as e:
            # FIXME: Catch only what is needed
            print(e)
            return Response({"erorr" : True})


class RestLinkedinLoginView(APIView):
    """
        Login or register a user based on an authentication token coming
        from Linkedin.
        Returns user data including session id.
    """
    permission_classes = (AllowAny,)
    authentication_classes = (PublicAuthentication,)

    def dispatch(self, *args, **kwargs):
        return super(RestLinkedinLoginView, self).dispatch(*args, **kwargs)

    def post(self, request, format=None):
        
        try:
            app = SocialApp.objects.get(provider="linkedin_oauth2")
            adapter = LinkedInOAuth2Adapter(request)
            callback_url = 'http://localhost:3000/'
            provider = adapter.get_provider()
            scope = provider.get_scope(request)
            client = OAuth2Client(self.request, app.client_id, app.secret,
                              adapter.access_token_method,
                              adapter.access_token_url,
                              callback_url,
                              scope,
                              scope_delimiter=adapter.scope_delimiter,
                              headers=adapter.headers,
                              basic_auth=adapter.basic_auth)
            data = self.request.data
            code = data.get('code', '')
            access_token = client.get_access_token(code)
            token = adapter.parse_token(access_token)
            token.app = app
            login = adapter.complete_login(request,
                                                app,
                                                token,
                                                response=access_token)
            login.token = token
            complete_social_login(request, login)
            logged_in_user = login.account.user
            token, created= TokenModel.objects.get_or_create(user=logged_in_user)
            return Response({"success" : True, 'key' : token.key})
        except Exception as e:
            # FIXME: Catch only what is needed
            print(e)
            return Response({"erorr" : True})
