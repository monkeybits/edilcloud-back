from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.linkedin_oauth2.views import LinkedInOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_auth.models import TokenModel


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
