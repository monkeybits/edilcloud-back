# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from apps.profile import models
from web.utils import config


User = get_user_model()


class UserMixin(object):
    def perform_create(self, serializer):
        serializer.save(
            creator=self.request.user,
            last_modifier=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(
            last_modifier=self.request.user
        )

    def get_user(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None


class CompanyMixin(object):
    def get_company(self, company_id):
        """
        :param company_id: id company
        :return: company instance if it is exists
        """
        return get_object_or_404(models.Company.objects.filter(status=1, id=company_id))

    def check_self_invitation(self, company_id):
        """
        Check whether profile is following own company or not
        """
        companies = models.Company.objects.filter(
            creator=self.request.user,
            id=company_id
        )
        if companies.exists():
            raise PermissionDenied(config['ERROR']['SelfCompanyInvitation'])


class ProfileMixin(object):
    """
    Get user information: for example Company, Role, etc.
    """

    # def get_tracking(self, request):
    #     user = request.user
    #     try:
    #         return user.auth_token.tracking
    #     except:
    #         return None

    def get_profile_by_id(self, profile_id, profile_status=1):
        """
        :param profile_id: id profile
        :param profile_status: status profile
        :return: profile instance if it is exists
        """
        return get_object_or_404(models.Profile.objects.filter(status=profile_status, id=profile_id))

    def check_profile(self, request):
        """
        Check whether main profile already exists or not.
        """

        profiles = request.user.profiles.filter(company__isnull=True)
        if profiles.exists():
            raise PermissionDenied(config['ERROR']['MultipleMainProfiles'])

    def check_company_profile(self, tracking, user_id):
        """
        Check whether company profile already exists or not w.r.t. company, user
        """
        # TODO: to think
        profiles = models.Profile.objects.filter(
            company_id=tracking.profile.company_id,
            user_id=user_id
        )
        if profiles.exists():
            raise PermissionDenied(config['ERROR']['CompanyProfileExist'])

    def check_company_profile_by_email(self, tracking, email):
        """
        Check whether company profile already exists or not w.r.t. company, email
        """
        if email:
            profiles = models.Profile.objects.filter(
                company_id=tracking.profile.company_id,
                email=email
            )
            if profiles.exists():
                raise PermissionDenied(config['ERROR']['CompanyProfileExist'])

    def check_company_invitation_profile(self):
        """
        Check whether company profile already exists or not w.r.t. company
        """
        profiles = self.request.user.invitations.filter(
            company_id=self.kwargs.get('pk', None)
        )
        if profiles.exists():
            raise PermissionDenied(config['ERROR']['MultipleCompanyProfiles'])

    # def get_main_profile(self, user):
    #     """
    #     This is for cloning profile details
    #     :return:
    #     """
    #     try:
    #         return user.get_main_profile()
    #     except models.Profile.MultipleObjectsReturned:
    #         raise PermissionDenied(config['ERROR']['MultipleObjectsReturned'])
    #     except:
    #         raise PermissionDenied(config['ERROR']['MainProfileMissing'])

    def get_user(self):
        try:
            return User.objects.get(
                pk=self.request.user.pk
            )
        except User.DoesNotExist:
            raise PermissionDenied(config['ERROR']['UserNotExist'])
