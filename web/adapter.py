import os
import urllib
from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import resolve_url
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import get_adapter as get_account_adapter
from django.template.defaultfilters import slugify
from django.core.files.base import ContentFile
from django.dispatch import receiver


class AccountAdapter(DefaultAccountAdapter):
    """
        Custom account adapter to add some extra values to default 
    """

    def get_login_redirect_url(self, request):

        """
        	Override get_login_redirect_url to get dynamic redirect url
        """
        path = "/"
        return path


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom socialaccount adapter to add some extra values to default 
    """

    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login. In case of auto-signup,
        the signup form is not available.
        """
        user = super(SocialAccountAdapter, self).save_user(request, sociallogin, form=form)

    def is_auto_signup_allowed(self, request, sociallogin):
        '''
        	Override is_auto_signup_allowed
        '''
        return True