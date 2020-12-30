# -*- coding: utf-8 -*-

import datetime
import json
import operator
from functools import reduce

from django.db.models import Q
from django.utils.http import base36_to_int
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import generics, status, exceptions

from apps.message.api.frontend import serializers as message_serializers
from apps.media.api.frontend import serializers as media_serializers
from apps.product.models import Category
from apps.profile.models import Company
from apps.project.api.frontend import serializers as project_serializers
from apps.profile.api.frontend import serializers as profile_serializers
from apps.project.models import Project
from apps.quotation.api.frontend import serializers as quotation_serializers
from apps.document.api.frontend import serializers as document_serializers
from web.api.permissions import RoleAccessPermission
from web.api.views import (
    QuerysetMixin,
    JWTPayloadMixin,
    WhistleGenericViewMixin
)
from apps.profile.api.frontend import serializers
from apps.profile import models
from web.drf import exceptions as django_api_exception


class TrackerCompanyProfileMixin(
        JWTPayloadMixin):
    """
    Company Profile Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            generic_profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            profile = generic_profile.get_profile(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, profile)
            return profile
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.ProfileSerializer
        else:
            self.serializer_class = output_serializer


class CompanyListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all companies
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.CompanySerializer

    def __init__(self, *args, **kwargs):
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'url', 'email', 'phone',
            'logo', 'followed', 'is_supplier', 'partnership'
        ]
        super(CompanyListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        self.queryset = models.Company.objects.active()
        return super(CompanyListView, self).get_queryset().filter()


class TrackerProfileAcceptInviteView(
        generics.UpdateAPIView):
    """
    Accept the invitation request from a company
    """
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileAcceptInvitationEditSerializer

    def __init__(self, *args, **kwargs):
        self.profile_request_include_fields = []
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'company', 'user',
            'email', 'company_invitation_date', 'profile_invitation_date',
            'invitation_refuse_date', 'phone', 'language',
            'position', 'role', 'status', 'photo', 'fax', 'mobile', 'note', 'is_main', 'is_shared', 'is_in_showroom'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'url',
            'ssn', 'logo'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(TrackerProfileAcceptInviteView, self).__init__(*args, **kwargs)

    def get_object(self):
        base_36 = self.kwargs.get('base36')
        token = self.kwargs.get('token')
        id = base36_to_int(base_36)
        profile = get_object_or_404(
            self.get_queryset().filter(pk=id)
        )
        check = profile.check_token(token)
        if not check:
            raise django_api_exception.ProfileAPIDoesNotMatch(
                status.HTTP_403_FORBIDDEN, self.request, _('No profile matches the given query')
            )
        if not profile.user:
        # if profile.user and profile.user != self.request.user:
            raise django_api_exception.ProfileAPIDoesNotMatch(
                status.HTTP_403_FORBIDDEN, self.request, _('Profiles don\'t match')
            )
        return profile


class TrackerProfileRefuseInviteView(
        generics.UpdateAPIView):
    """
    Refuse the invitation request from a company
    """
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileRefuseInvitationEditSerializer

    def __init__(self, *args, **kwargs):
        self.profile_request_include_fields = []
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'company', 'user',
            'email', 'company_invitation_date', 'profile_invitation_date',
            'invitation_refuse_date', 'phone', 'language',
            'position', 'role', 'status', 'photo', 'fax', 'mobile', 'note', 'is_main', 'is_shared', 'is_in_showroom'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'url',
            'ssn', 'logo'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(TrackerProfileRefuseInviteView, self).__init__(*args, **kwargs)

    def get_object(self):
        base_36 = self.kwargs.get('base36')
        token = self.kwargs.get('token')
        id = base36_to_int(base_36)
        profile = get_object_or_404(
            self.get_queryset().filter(pk=id)
        )
        check = profile.check_token(token)
        if not check:
            raise django_api_exception.ProfileAPIDoesNotMatch(
                status.HTTP_403_FORBIDDEN, self.request, _('No profile matches the given query')
            )
        if not profile.user:
        # if profile.user and profile.user != self.request.user:
            raise django_api_exception.ProfileAPIDoesNotMatch(
                status.HTTP_403_FORBIDDEN, self.request, _('Profiles don\'t match')
            )
        return profile


class TrackerProfileReAcceptInviteView(
        generics.UpdateAPIView):
    """
    Accept the invitation request from a company
    """
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileReAcceptInvitationEditSerializer

    def __init__(self, *args, **kwargs):
        self.profile_request_include_fields = []
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'company', 'user',
            'email', 'company_invitation_date', 'profile_invitation_date',
            'invitation_refuse_date', 'phone', 'language',
            'position', 'role', 'status', 'photo', 'fax', 'mobile', 'note', 'is_main', 'is_shared', 'is_in_showroom'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'url',
            'ssn', 'logo'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(TrackerProfileReAcceptInviteView, self).__init__(*args, **kwargs)


class TrackerProfileChangeShowroomVisibilityView(
        generics.UpdateAPIView):
    """
    Accept the invitation request from a company
    """
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileChangeShowroomVisibilitySerializer

    def __init__(self, *args, **kwargs):
        self.profile_request_include_fields = []
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'company', 'user',
            'email', 'company_invitation_date', 'profile_invitation_date',
            'invitation_refuse_date', 'phone', 'language',
            'position', 'role', 'status', 'photo', 'fax', 'mobile', 'note', 'is_main',
            'is_shared', 'is_in_showroom'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'url',
            'ssn', 'logo'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(TrackerProfileChangeShowroomVisibilityView, self).__init__(*args, **kwargs)


class TrackerProfileChangeComunicaVisibilityView(
        generics.UpdateAPIView):
    """
    Accept the invitation request from a company
    """
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileChangeComunicaVisibilitySerializer

    def __init__(self, *args, **kwargs):
        self.profile_request_include_fields = []
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'company', 'user',
            'email', 'company_invitation_date', 'profile_invitation_date',
            'invitation_refuse_date', 'phone', 'language',
            'position', 'role', 'status', 'photo', 'fax', 'mobile', 'note', 'is_main',
            'is_shared', 'is_in_showroom'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'url',
            'ssn', 'logo'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(TrackerProfileChangeComunicaVisibilityView, self).__init__(*args, **kwargs)


class TrackerProfileDocumentListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all profile documents
    """

    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = document_serializers.DocumentSerializer

    def __init__(self, *args, **kwargs):
        self.document_response_include_fields = ['id', 'title', 'description', 'document', 'date_create', 'size', 'extension']
        super(TrackerProfileDocumentListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            profile = self.request.user.get_profile_by_id(self.kwargs.get('pk'))
            self.queryset = profile.list_profile_documents()
            return super(TrackerProfileDocumentListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProjectAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProfilePreferenceMixin(
        JWTPayloadMixin):
    """
    Profile Preference Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            preference = profile.get_preference()
            self.check_object_permissions(self.request, preference)
            return preference
        except ObjectDoesNotExist as err:
            raise django_api_exception.PreferenceAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerPreferenceDetailView(
        TrackerProfilePreferenceMixin,
        generics.RetrieveAPIView):
    """
    Detail a profile preference
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.PreferenceSerializer


class TrackerPreferenceEditView(
        TrackerProfilePreferenceMixin,
        generics.RetrieveUpdateAPIView):
    """
    Update a profile preference
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.PreferenceEditSerializer


class TrackerCompanyProfileAddView(
    WhistleGenericViewMixin,
    TrackerCompanyProfileMixin,
    generics.CreateAPIView):
    """
    Create a user profile (May be, it could be a phantom)
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.ProfileAddSerializer

    def __init__(self, *args, **kwargs):
        self.profile_request_include_fields = [
            'first_name', 'last_name', 'email',
            'language', 'position', 'user', 'phone',
            'fax', 'mobile', 'note', 'role',
            'can_access_files', 'can_access_chat'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email',
            'language', 'position', 'photo', 'role', 'is_shared', 'is_in_showroom',
            'can_access_files', 'can_access_chat', 'is_invited'
        ]
        super(TrackerCompanyProfileAddView, self).__init__(*args, **kwargs)


class TrackerCompanyInviteProfileAddView(
        WhistleGenericViewMixin,
        TrackerCompanyProfileMixin,
        generics.CreateAPIView):
    """
    Create a company profile
    # Todo: Check the workflow
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileAddSerializer

    def __init__(self, *args, **kwargs):
        # self.profile_request_include_fields = [
        #     'user', 'position', 'role', 'company_invitation_date'
        # ]
        self.profile_request_include_fields = [
            'first_name', 'last_name', 'email',
            'language', 'position', 'user', 'phone',
            'fax', 'mobile', 'note', 'role',
            'can_access_files', 'can_access_chat'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email',
            'language', 'position', 'photo', 'role', 'is_shared', 'is_in_showroom',
            'can_access_files', 'can_access_chat'
        ]
        super(TrackerCompanyInviteProfileAddView, self).__init__(*args, **kwargs)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {'pk': self.kwargs.get('pk', None)}
        return get_object_or_404(queryset, **filter_kwargs)

    def post(self, request, *args, **kwargs):
        invitation = self.get_object()
        if not request.POST._mutable:
            request.POST._mutable = True

        request.data['user'] = invitation.user.id
        request.data['role'] = request.data['role'] or settings.LEVEL_2
        request.data['company_invitation_date'] = datetime.datetime.now()
        return self.create(request, *args, **kwargs)

class TrackerCompanyProfileListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all profiles
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user', 'is_shared',
                                                'is_in_showroom',             'can_access_files', 'can_access_chat']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn',             'can_access_files', 'can_access_chat']
        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(TrackerCompanyProfileListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_profiles()
        return super(TrackerCompanyProfileListView, self).get_queryset()


class TrackerCompanyProfileDetailView(
        WhistleGenericViewMixin,
        TrackerCompanyProfileMixin,
        generics.RetrieveAPIView):
    """
    Company can show company profile
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email',
            'language', 'position', 'role', 'fax',
            'mobile', 'note', 'phone', 'photo', 'is_shared', 'is_in_showroom',
            'company_invitation_date', 'profile_invitation_date', 'talk_count',
            'can_access_files', 'can_access_chat', 'user', 'preference'
        ]
        self.user_response_include_fields = ['id', 'first_name', 'last_name', 'username']
        super(TrackerCompanyProfileDetailView, self).__init__(*args, **kwargs)


class TrackerCompanyProfileEditView(
        WhistleGenericViewMixin,
        TrackerCompanyProfileMixin,
        generics.RetrieveUpdateAPIView):
    """
    Company can edit company profile
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, settings.LEVEL_2)
    serializer_class = serializers.ProfileEditSerializer

    def __init__(self, *args, **kwargs):
        self.profile_request_include_fields = [
            'first_name', 'last_name', 'email',
            'language', 'position', 'user', 'phone',
            'fax', 'mobile', 'note', 'role', 'photo', 'can_access_files', 'can_access_chat'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'language', 'fax', 'company', 'user', 'role', 'position',
            'status', 'uidb36', 'token', 'photo', 'company_invitation_date',
            'profile_invitation_date', 'invitation_refuse_date', 'is_shared', 'is_in_showroom',
            'can_access_files', 'can_access_chat'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn', 'logo'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(TrackerCompanyProfileEditView, self).__init__(*args, **kwargs)


class TrackerCompanyProfileEnableView(
        TrackerCompanyProfileMixin,
        generics.RetrieveUpdateAPIView):
    """
    Company can enable profile
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.ProfileEnableSerializer

    def __init__(self, *args, **kwargs):
        self.profile_request_include_fields = []
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email',
            'language', 'position', 'is_shared', 'is_in_showroom',
            'can_access_files', 'can_access_chat'
        ]
        super(TrackerCompanyProfileEnableView, self).__init__(*args, **kwargs)


class TrackerCompanyProfileDisableView(
        TrackerCompanyProfileMixin,
        generics.RetrieveUpdateAPIView):
    """
    Company can disable profile
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.ProfileDisableSerializer

    def __init__(self, *args, **kwargs):
        self.profile_request_include_fields = []
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email',
            'language', 'position', 'is_shared', 'is_in_showroom'
        ]
        super(TrackerCompanyProfileDisableView, self).__init__(*args, **kwargs)


class TrackerCompanyProfileDeleteView(
        TrackerCompanyProfileMixin,
        generics.RetrieveDestroyAPIView):
    """
    Company can disable profile
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_request_include_fields = []
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'company', 'user', 'is_shared', 'is_in_showroom'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn', 'logo'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(TrackerCompanyProfileDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_profile(instance)


class FollowCompanyMixin(
        JWTPayloadMixin):
    """
    Company Mixin
    """
    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.FavouriteSerializer
        else:
            self.serializer_class = output_serializer


class TrackerCompanyFollowView(
        WhistleGenericViewMixin,
        FollowCompanyMixin,
        generics.CreateAPIView):
    """
    Follow a company
    """
    serializer_class = serializers.SetFavouriteSerializer

    def __init__(self, *args, **kwargs):
        self.favourite_request_include_fields = [
            'company'
        ]
        self.favourite_response_include_fields = [
            'id', 'company'
        ]
        self.company_response_include_fields = [
            'id',
        ]
        super(TrackerCompanyFollowView, self).__init__(*args, **kwargs)


class TrackerCompanyUnFollowView(
        generics.RetrieveDestroyAPIView):
    """
    Unfollow a company
    """
    queryset = models.Favourite.objects.all()
    serializer_class = serializers.FavouriteSerializer
    lookup_field = 'company_id'

    def perform_destroy(self, instance):
        main_profile = self.request.user.get_main_profile()
        main_profile.unfollow_company(instance.company)

    def get_queryset(self):
        main_profile = self.request.user.get_main_profile()
        return models.Favourite.objects.filter(profile=main_profile)


class TrackerCompanyAcceptFollowView(
        WhistleGenericViewMixin,
        FollowCompanyMixin,
        QuerysetMixin,
        generics.RetrieveUpdateAPIView):
    """
    Follow a company
    """
    queryset = models.Company.objects.all()
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.FavouriteAcceptSerializer

    def __init__(self, *args, **kwargs):
        self.favourite_request_include_fields = [
            'company'
        ]
        self.favourite_response_include_fields = [
            'id'
        ]
        super(TrackerCompanyAcceptFollowView, self).__init__(*args, **kwargs)


class TrackerCompanyRefuseFollowView(
        FollowCompanyMixin,
        QuerysetMixin,
        generics.RetrieveDestroyAPIView):
    """
        Get all partnership
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.FavouriteSerializer
    lookup_field = 'company_id'
    lookup_url_kwarg = 'company'

    def __init__(self, *args, **kwargs):
        self.favourite_request_include_fields = [
            'company'
        ]
        self.favourite_response_include_fields = [
            'id',
        ]
        super(TrackerCompanyRefuseFollowView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = self.profile.list_received_favourites()
        return super(TrackerCompanyRefuseFollowView, self).get_queryset()

    def perform_destroy(self, instance):
        self.profile.remove_follower(instance)


class TrackerCompanyMixin(
        JWTPayloadMixin):
    """
    Company Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            company = profile.get_company(profile.company_id)
            self.check_object_permissions(self.request, company)
            return company
        except ObjectDoesNotExist as err:
            raise django_api_exception.CompanyAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.CompanySerializer
        else:
            self.serializer_class = output_serializer


class TrackerCompanyDetailView(
        TrackerCompanyMixin,
        generics.RetrieveAPIView):
    """
    Detail a single company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.CompanySerializer

    def __init__(self, *args, **kwargs):
        self.company_response_include_fields = [
            'id', 'name', 'brand', 'description', 'slug', 'email', 'ssn',
            'email', 'phone', 'logo', 'vat_number',
            'url', 'fax', 'phone2', 'projects_count',
            'messages_count', 'tags_count', 'followers_count',
            'staff_count', 'partnerships_count', 'category', 'is_sponsor',
            'can_access_files', 'can_access_chat', 'talks', 'last_message_created', 'customer', 'trial_used', 'subscription'
        ]
        self.talk_response_include_fields = [
            'id', 'code', 'unread_count'
        ]
        super(TrackerCompanyDetailView, self).__init__(*args, **kwargs)


class TrackerPartnershipMixin(
        JWTPayloadMixin):
    """
    Partnership Mixin
    """
    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.PartnershipSerializer
        else:
            self.serializer_class = output_serializer


class TrackerCompanyPartnerShipListView(
        TrackerCompanyMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
        Get all partnership
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.PartnershipSerializer

    def __init__(self, *args, **kwargs):
        self.partnership_response_include_fields = [
            'id', 'guest_company', 'inviting_company', 'invitation_date',
            'approval_date', 'refuse_date'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'logo', 'url', 'email', 'phone',
            'phone2', 'fax', 'is_supplier'
        ]
        super(TrackerCompanyPartnerShipListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        generic = 'list_' + self.kwargs.get('type') + '_partnerships'
        self.queryset = getattr(profile, generic)()
        return super(TrackerCompanyPartnerShipListView, self).get_queryset()


class TrackerCompanyPartnerShipAddView(
        WhistleGenericViewMixin,
        TrackerPartnershipMixin,
        QuerysetMixin,
        generics.CreateAPIView):
    """
        Create partnership
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.PartnershipAddSerializer

    def __init__(self, *args, **kwargs):
        self.partnership_request_include_fields = []
        self.partnership_response_include_fields = [
            'id', 'guest_company', 'inviting_company', 'invitation_date',
            'approval_date', 'refuse_date'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'logo', 'url', 'email', 'phone',
            'phone2', 'fax', 'is_supplier'
        ]
        super(TrackerCompanyPartnerShipAddView, self).__init__(*args, **kwargs)


class TrackerCompanyPartnerShipAcceptView(
        WhistleGenericViewMixin,
        TrackerPartnershipMixin,
        QuerysetMixin,
        generics.RetrieveUpdateAPIView):
    """
        Get all partnership
    """
    queryset = models.Company.objects.all()
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.PartnershipAcceptSerializer

    def __init__(self, *args, **kwargs):
        self.partnership_request_include_fields = []
        self.partnership_response_include_fields = [
            'id', 'guest_company', 'inviting_company', 'invitation_date',
            'approval_date', 'refuse_date'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'logo', 'url', 'email', 'phone',
            'phone2', 'fax', 'is_supplier'
        ]
        super(TrackerCompanyPartnerShipAcceptView, self).__init__(*args, **kwargs)


class TrackerCompanyPartnerShipRefuseView(
        TrackerPartnershipMixin,
        QuerysetMixin,
        generics.RetrieveDestroyAPIView):
    """
        Get all partnership
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.PartnershipSerializer

    def __init__(self, *args, **kwargs):
        self.partnership_request_include_fields = []
        self.partnership_response_include_fields = [
            'id', 'guest_company', 'inviting_company', 'invitation_date',
            'approval_date', 'refuse_date'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'logo', 'url', 'email', 'phone',
            'phone2', 'fax', 'is_supplier'
        ]
        super(TrackerCompanyPartnerShipRefuseView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = self.profile.list_created_partnerships()
        return super(TrackerCompanyPartnerShipRefuseView, self).get_queryset()

    def perform_destroy(self, instance):
        self.profile.remove_partnership(instance)


class TrackerCompanyDeleteView(
        TrackerCompanyMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a single company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.CompanySerializer

    def __init__(self, *args, **kwargs):
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn',
            'email', 'phone', 'logo'
        ]
        super(TrackerCompanyDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_company()


class TrackerCompanyEditView(
        WhistleGenericViewMixin,
        TrackerCompanyMixin,
        generics.RetrieveUpdateAPIView):
    """
    Update a single company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.CompanyEditSerializer

    def __init__(self, *args, **kwargs):
        self.company_request_include_fields = [
            'name', 'slug', 'brand', 'description', 'ssn',
            'vat_number', 'url',
            'email', 'phone', 'phone2', 'fax',
            'note', 'logo', 'category',
            'color'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'brand', 'description', 'ssn',
            'vat_number', 'url',
            'email', 'phone', 'phone2', 'fax',
            'note', 'logo', 'category',
            'color'
        ]
        super(TrackerCompanyEditView, self).__init__(*args, **kwargs)

    def put(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True
        if 'category' in request.data:
            category_field = {}
            if isinstance(request.data['category'], str):
                category_list = request.data['category'].split(',')
                qs = Category.objects.filter(code__in=category_list)
                for row in qs:
                    category_field[row.code] = row.name
                request.data['category'] = json.dumps(category_field)
            else:
                qs = Category.objects.filter(code__in=request.data['category'])
                for row in qs:
                    category_field[row.code] = row.name
                request.data['category'] = category_field
        return super(TrackerCompanyEditView, self).put(request, *args, **kwargs)


class TrackerCompanyEnableView(
        TrackerCompanyMixin,
        generics.RetrieveUpdateAPIView):
    """
    Enable a single company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.CompanyEnableSerializer

    def __init__(self, *args, **kwargs):
        self.company_request_include_fields = []
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn',
            'email', 'phone', 'logo'
        ]
        super(TrackerCompanyEnableView, self).__init__(*args, **kwargs)


class TrackerCompanyDisableView(
        TrackerCompanyMixin,
        generics.RetrieveUpdateAPIView):
    """
    Disable a single company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.CompanyDisableSerializer

    def __init__(self, *args, **kwargs):
        self.company_request_include_fields = []
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn',
            'email', 'phone', 'logo'
        ]
        super(TrackerCompanyDisableView, self).__init__(*args, **kwargs)


class TrackerCompanyDocumentListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all documents
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = document_serializers.DocumentSerializer

    def __init__(self, *args, **kwargs):
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document',
            'date_create', 'date_last_modify', 'status',
        ]
        super(TrackerCompanyDocumentListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_documents()
        return super(TrackerCompanyDocumentListView, self).get_queryset()


class TrackerCompanyMessageListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
        Get all project messages
        """
    serializer_class = message_serializers.MessageSerializer

    def __init__(self, *args, **kwargs):
        self.message_response_include_fields = [
            'id', 'body', 'sender', 'date_create', 'files', 'unique_code', 'read'
        ]
        self.talk_response_include_fields = ['id', 'code', 'content_type_name']
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'is_shared', 'is_in_showroom', 'position', 'company'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'category', 'color_project'
        ]
        super(TrackerCompanyMessageListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_company_messages()
        messages = super(TrackerCompanyMessageListView, self).get_queryset()
        if 'type' in self.kwargs and self.kwargs['type'] == 'last':
            limit = settings.REST_FRAMEWORK['PAGE_SIZE']
            if 'per_page' in self.request.GET:
                limit = int(self.request.GET['per_page'])
            if messages.count() > limit:
                offset = messages.count() - limit
                return messages[offset:messages.count()]
            return messages
        else:
            return messages


class TrackerCompanyCompanyDocumentListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company documents
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = document_serializers.DocumentSerializer

    def __init__(self, *args, **kwargs):
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document',
            'date_create', 'date_last_modify', 'status',
            'extension', 'size', 'relative_path', 'folder_relative_path'
        ]
        super(TrackerCompanyCompanyDocumentListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        if 'type' in self.kwargs:
            list_method = 'list_{}_company_documents'.format(self.kwargs['type'])
            self.queryset = getattr(profile, list_method)()
        else:
            self.queryset = profile.list_company_documents()
        return super(TrackerCompanyCompanyDocumentListView, self).get_queryset()


class TrackerCompanyProjectDocumentListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company project documents
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = document_serializers.DocumentSerializer

    def __init__(self, *args, **kwargs):
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document',
            'date_create', 'date_last_modify', 'status',
            'extension'
        ]
        super(TrackerCompanyProjectDocumentListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_project_documents()
        return super(TrackerCompanyProjectDocumentListView, self).get_queryset()


class TrackerCompanyProfileDocumentListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company profile documents
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = document_serializers.DocumentSerializer

    def __init__(self, *args, **kwargs):
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document',
            'date_create', 'date_last_modify', 'status',
            'extension'
        ]
        super(TrackerCompanyProfileDocumentListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_profile_documents()
        return super(TrackerCompanyProfileDocumentListView, self).get_queryset()


class TrackerCompanyBomDocumentListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company bom documents
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = document_serializers.DocumentSerializer

    def __init__(self, *args, **kwargs):
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document',
            'date_create', 'date_last_modify', 'status',
            'extension'
        ]
        super(TrackerCompanyBomDocumentListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_bom_documents()
        return super(TrackerCompanyBomDocumentListView, self).get_queryset()


class TrackerCompanyTalkListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all talks
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = message_serializers.TalkSerializer

    def __init__(self, *args, **kwargs):
        self.talk_response_include_fields = ['id', 'code', 'content_type_name']
        super(TrackerCompanyTalkListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_talks()
        return super(TrackerCompanyTalkListView, self).get_queryset()


class TrackerCompanyCompanyTalkListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company talks
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = message_serializers.TalkSerializer

    def __init__(self, *args, **kwargs):
        self.talk_response_include_fields = ['id', 'code']
        super(TrackerCompanyCompanyTalkListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_company_talks()
        return super(TrackerCompanyCompanyTalkListView, self).get_queryset()


class TrackerCompanyProjectTalkListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company project talks
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = message_serializers.TalkSerializer

    def __init__(self, *args, **kwargs):
        self.talk_response_include_fields = ['id', 'code']
        super(TrackerCompanyProjectTalkListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_project_talks()
        return super(TrackerCompanyProjectTalkListView, self).get_queryset()


class TrackerCompanyProfileTalkListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company profile talks
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = message_serializers.TalkSerializer

    def __init__(self, *args, **kwargs):
        self.talk_response_include_fields = ['id', 'code']
        super(TrackerCompanyProfileTalkListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_profile_talks()
        return super(TrackerCompanyProfileTalkListView, self).get_queryset()


class TrackerCompanyPhotoListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company photos
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = media_serializers.PhotoSerializer

    def __init__(self, *args, **kwargs):
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo', 'extension',
            'photo_64'
        ]
        super(TrackerCompanyPhotoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_photos()
        return super(TrackerCompanyPhotoListView, self).get_queryset()


class TrackerCompanyCompanyPhotoListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company photos
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles =settings.MEMBERS
    serializer_class = media_serializers.PhotoSerializer

    def __init__(self, *args, **kwargs):
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo', 'extension',
             'note', 'is_public', 'size', 'relative_path', 'folder_relative_path'
        ]
        super(TrackerCompanyCompanyPhotoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        if 'type' in self.kwargs:
            list_method = 'list_{}_company_photos'.format(self.kwargs['type'])
            self.queryset = getattr(profile, list_method)()
        else:
            self.queryset = profile.list_company_photos()
        return super(TrackerCompanyCompanyPhotoListView, self).get_queryset()

class TrackerCompanyTotalPhotoSizeListView(JWTPayloadMixin, QuerysetMixin, generics.ListAPIView):
    """
    Get total photo size
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = media_serializers.PhotoSerializer

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        if 'type' in self.kwargs:
            list_method = 'list_{}_company_photos'.format(self.kwargs['type'])
            self.queryset = getattr(profile, list_method)()
        else:
            self.queryset = profile.list_company_photos()
        return super(TrackerCompanyTotalPhotoSizeListView, self).get_queryset()

    def list(self, request, *args, **kwargs):
        total_size = 0
        for object in self.get_queryset():
            total_size += object.photo.size
        return Response([
            {
                'total': total_size,
                'uom': 'bytes'
            },
            {
                'total': total_size / 1000,
                'uom': 'kilobytes'
            },
            {
                'total': (total_size / 1000) /1000,
                'uom': 'megabytes'
            },
            {
                'total': ((total_size / 1000) / 1000) / 1000,
                'uom': 'gigabytes'
            }
        ])

class TrackerCompanyProjectPhotoListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company project photos
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = media_serializers.PhotoSerializer

    def __init__(self, *args, **kwargs):
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo', 'is_public'
        ]
        super(TrackerCompanyProjectPhotoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_project_photos()
        return super(TrackerCompanyProjectPhotoListView, self).get_queryset()


class TrackerCompanyBomPhotoListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company bom photos
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = media_serializers.PhotoSerializer

    def __init__(self, *args, **kwargs):
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo', 'extension',
            'photo_64', 'is_public'
        ]
        super(TrackerCompanyBomPhotoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_bom_photos()
        return super(TrackerCompanyBomPhotoListView, self).get_queryset()


class TrackerCompanyVideoListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company Videos
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = media_serializers.VideoSerializer

    def __init__(self, *args, **kwargs):
        self.video_response_include_fields = [
            'id', 'title', 'pub_date', 'video',
            'extension', 'is_public', 'size'
        ]
        super(TrackerCompanyVideoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_videos()
        return super(TrackerCompanyVideoListView, self).get_queryset()

class TrackerCompanyTotalVideoSizeListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
       Get all company Videos
       """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = media_serializers.VideoSerializer

    def __init__(self, *args, **kwargs):
        self.video_response_include_fields = [
            'id', 'title', 'pub_date', 'video',
            'extension', 'is_public'
        ]
        super(TrackerCompanyTotalVideoSizeListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_videos()
        return super(TrackerCompanyTotalVideoSizeListView, self).get_queryset()

    def list(self, request, *args, **kwargs):
        total_size = 0
        for object in self.get_queryset():
            total_size += object.video.size
        return Response([
            {
                'total': total_size,
                'uom': 'bytes'
            },
            {
                'total': total_size / 1000,
                'uom': 'kilobytes'
            },
            {
                'total': (total_size / 1000) /1000,
                'uom': 'megabytes'
            },
            {
                'total': ((total_size / 1000) / 1000) / 1000,
                'uom': 'gigabytes'
            }
        ])

class TrackerCompanyCompanyVideoListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company Videos
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = media_serializers.VideoSerializer

    def __init__(self, *args, **kwargs):
        self.video_response_include_fields = [
            'id', 'title', 'pub_date', 'video',
            'extension', 'note', 'is_public', 'size', 'relative_path', 'folder_relative_path'
        ]
        super(TrackerCompanyCompanyVideoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        if 'type' in self.kwargs:
            list_method = 'list_{}_company_videos'.format(self.kwargs['type'])
            self.queryset = getattr(profile, list_method)()
        else:
            self.queryset = profile.list_company_videos()
        return super(TrackerCompanyCompanyVideoListView, self).get_queryset()


class TrackerCompanyProjectVideoListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company project Videos
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = media_serializers.VideoSerializer

    def __init__(self, *args, **kwargs):
        self.video_response_include_fields = [
            'id', 'title', 'pub_date', 'video', 'extension',
            'is_public'
        ]
        super(TrackerCompanyProjectVideoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_project_videos()
        return super(TrackerCompanyProjectVideoListView, self).get_queryset()


class TrackerCompanyBomVideoListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company bom Videos
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = media_serializers.VideoSerializer

    def __init__(self, *args, **kwargs):
        self.video_response_include_fields = [
            'id', 'title', 'pub_date', 'video', 'extension',
            'is_public'
        ]
        super(TrackerCompanyBomVideoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_bom_videos()
        return super(TrackerCompanyBomVideoListView, self).get_queryset()


class TrackerCompanyBomListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company bill of materials
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = quotation_serializers.BomSerializer

    def __init__(self, *args, **kwargs):
        self.bom_response_include_fields = ['id', 'title', 'description', 'owner', 'contact', 'date_bom', 'deadline']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn']
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'is_shared', 'is_in_showroom']
        super(TrackerCompanyBomListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_boms()
        return super(TrackerCompanyBomListView, self).get_queryset()


class TrackerCompanyQuotationListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company quotations
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = quotation_serializers.QuotationSerializer

    def __init__(self, *args, **kwargs):
        self.quotation_response_include_fields = [
            'id', 'title', 'description', 'owner', 'contact', 'date_quotation',
            'deadline', 'bom', 'tags'
        ]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn']
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'is_shared', 'is_in_showroom']
        self.bom_response_include_fields = ['id', 'title', 'description', 'date_bom', 'deadline']
        super(TrackerCompanyQuotationListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_quotations()
        return super(TrackerCompanyQuotationListView, self).get_queryset()


class TrackerCompanyOfferListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company offers
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = quotation_serializers.OfferSerializer

    def __init__(self, *args, **kwargs):
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date', 'deadline',
            'price', 'contact', 'owner', 'tags'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'is_shared', 'is_in_showroom'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn', 'logo'
        ]
        super(TrackerCompanyOfferListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_offers()
        return super(TrackerCompanyOfferListView, self).get_queryset()


class TrackerCompanyActiveOfferListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company offers
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = quotation_serializers.OfferSerializer

    def __init__(self, *args, **kwargs):
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date', 'deadline', 'followers',
            'price', 'contact', 'owner', 'tags', 'photo', 'start_date'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'is_shared', 'is_in_showroom'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn', 'logo'
        ]
        super(TrackerCompanyActiveOfferListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_active_offers().filter(is_draft=False)
        return super(TrackerCompanyActiveOfferListView, self).get_queryset()


class TrackerCompanyCertificationListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company certificates
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = quotation_serializers.CertificationSerializer

    def __init__(self, *args, **kwargs):
        self.certification_response_include_fields = [
            'id', 'title', 'description', 'document', 'contact', 'owner',
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'is_shared', 'is_in_showroom'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn', 'logo'
        ]
        super(TrackerCompanyCertificationListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_certifications()
        return super(TrackerCompanyCertificationListView, self).get_queryset()


class TrackerCompanyPhantomListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all phantom profiles w.r.t. company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user',
                                                'is_shared', 'is_in_showroom']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn']
        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(TrackerCompanyPhantomListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_phantoms()
        return super(TrackerCompanyPhantomListView, self).get_queryset()


class TrackerCompanyGuestListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all guest profiles w.r.t. company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user',
                                                'is_shared', 'is_in_showroom']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn']
        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(TrackerCompanyGuestListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_guests()
        return super(TrackerCompanyGuestListView, self).get_queryset()


class TrackerCompanyStaffListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company staffs
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'mobile',
            'language', 'fax', 'company', 'user', 'role', 'position',
            'status', 'uidb36', 'token', 'photo', 'company_invitation_date',
            'profile_invitation_date', 'invitation_refuse_date', 'is_shared', 'is_in_showroom',
            'can_access_files', 'can_access_chat'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn', 'logo', 'is_supplier'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(TrackerCompanyStaffListView, self).__init__(*args, **kwargs)

    def get_filters(self):
        filters = super(TrackerCompanyStaffListView, self).get_filters()
        if filters:
            if len(filters) != 1:
                query = []
                for key, value in enumerate(filters):
                    query.append(tuple((value, filters[value])))
                return reduce(operator.or_, [Q(x) for x in query])
        return filters

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        generic = 'list_'+self.kwargs.get('type')+'_profiles'
        self.queryset = getattr(profile, generic)()
        if 'exclude__role__in' in self.request.query_params:
            params = self.request.query_params.get('exclude__role__in')
            self.queryset = self.queryset.exclude(role__in=params.split(','))
        return super(TrackerCompanyStaffListView, self).get_queryset()

class TrackerProjectStaffListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company staffs
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'mobile',
            'language', 'fax', 'company', 'user', 'role', 'position',
            'status', 'uidb36', 'token', 'photo', 'company_invitation_date',
            'profile_invitation_date', 'invitation_refuse_date', 'is_shared', 'is_in_showroom',
            'can_access_files', 'can_access_chat'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn', 'logo', 'is_supplier'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(TrackerCompanyStaffListView, self).__init__(*args, **kwargs)

    def get_filters(self):
        filters = super(TrackerProjectStaffListView, self).get_filters()
        if filters:
            if len(filters) != 1:
                query = []
                for key, value in enumerate(filters):
                    query.append(tuple((value, filters[value])))
                return reduce(operator.or_, [Q(x) for x in query])
        return filters

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        generic = 'list_'+self.kwargs.get('type')+'_profiles'
        self.queryset = getattr(profile, generic)()
        return super(TrackerProjectStaffListView, self).get_queryset().filter(status=1)


class TrackerCompanyStaffListAndExternalView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company staffs and external owner/delegate companies
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'mobile',
            'language', 'fax', 'company', 'user', 'role', 'position',
            'status', 'uidb36', 'token', 'photo', 'company_invitation_date',
            'profile_invitation_date', 'invitation_refuse_date', 'is_shared', 'is_in_showroom',
            'can_access_files', 'can_access_chat', 'is_external'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn', 'logo', 'is_supplier'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(TrackerCompanyStaffListAndExternalView, self).__init__(*args, **kwargs)

    def get_filters(self):
        filters = super(TrackerCompanyStaffListAndExternalView, self).get_filters()
        if filters:
            if len(filters) != 1:
                query = []
                for key, value in enumerate(filters):
                    query.append(tuple((value, filters[value])))
                return reduce(operator.or_, [Q(x) for x in query])
        return filters

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        generic = 'list_'+self.kwargs.get('type')+'_profiles_and_external'
        is_creator = None
        if 'project_id' in self.request.query_params:
            project_id = self.request.query_params.get('project_id')
            project = Project.objects.get(id=project_id)
            creator = project.creator
            if creator == profile.user:
                is_creator = True
            else:
                is_creator = False
        self.queryset = getattr(profile, generic)(is_creator, profile)
        return super(TrackerCompanyStaffListAndExternalView, self).get_queryset().filter(status=1)




class TrackerCompanyStaffListDisabledView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company staffs
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'mobile',
            'language', 'fax', 'company', 'user', 'role', 'position',
            'status', 'uidb36', 'token', 'photo', 'company_invitation_date',
            'profile_invitation_date', 'invitation_refuse_date', 'is_shared', 'is_in_showroom',
            'can_access_files', 'can_access_chat'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn', 'logo', 'is_supplier'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(TrackerCompanyStaffListDisabledView, self).__init__(*args, **kwargs)

    def get_filters(self):
        filters = super(TrackerCompanyStaffListDisabledView, self).get_filters()
        if filters:
            if len(filters) != 1:
                query = []
                for key, value in enumerate(filters):
                    query.append(tuple((value, filters[value])))
                return reduce(operator.or_, [Q(x) for x in query])
        return filters

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        generic = 'list_'+self.kwargs.get('type')+'_profiles_inactive'
        self.queryset = getattr(profile, generic)()
        return super(TrackerCompanyStaffListDisabledView, self).get_queryset().filter(status=0)

class TrackerCompanyPublicStaffListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all company owners list
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user', 'phone', 'mobile',
                                                'email', 'language', 'role', 'is_shared', 'is_in_showroom']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn']

        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(TrackerCompanyPublicStaffListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.company.get_active_public_staff()
        return super(TrackerCompanyPublicStaffListView, self).get_queryset()


class TrackerCompanyShowroomStaffListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all company owners list
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user', 'phone', 'mobile',
                                                'email', 'language', 'role', 'is_shared', 'is_in_showroom', 'photo']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn']

        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(TrackerCompanyShowroomStaffListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.company.get_active_showroom_staff()
        return super(TrackerCompanyShowroomStaffListView, self).get_queryset()


class TrackerCompanyOwnerListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company owners list
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProfileSerializer
    
    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user', 'phone', 'mobile',
                                                'email', 'language', 'is_shared', 'is_in_showroom']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn']

        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(TrackerCompanyOwnerListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_owners()
        return super(TrackerCompanyOwnerListView, self).get_queryset()


class TrackerCompanyDelegateListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company delegates list
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user', 'phone', 'mobile',
                                                'email', 'language', 'is_shared', 'is_in_showroom']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn']
        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(TrackerCompanyDelegateListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_delegates()
        return super(TrackerCompanyDelegateListView, self).get_queryset()


class TrackerCompanyLevel1ListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company level1 team members
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user',
                                                'is_shared', 'is_in_showroom']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn']
        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(TrackerCompanyLevel1ListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_level1s()
        return super(TrackerCompanyLevel1ListView, self).get_queryset()


class TrackerCompanyLevel2ListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company level2 team members
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user',
                                                'is_shared', 'is_in_showroom']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn']
        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(TrackerCompanyLevel2ListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_level2s()
        return super(TrackerCompanyLevel2ListView, self).get_queryset()


class TrackerCompanyProjectListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all projects wrt company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = project_serializers.ProjectSerializer

    def __init__(self, *args, **kwargs):
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
            'company', 'referent', 'status',
            'profiles', 'typology', 'completed',
            'shared_companies', 'logo', 'talks', 'last_message_created', 'address'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'is_shared', 'is_in_showroom'
        ]
        self.talk_response_include_fields = [
            'id', 'code', 'unread_count'
        ]
        super(TrackerCompanyProjectListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_projects()
        return super(TrackerCompanyProjectListView, self).get_queryset()


class TrackerCompanySimpleProjectListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all projects wrt company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = project_serializers.SimpleProjectSerializer

    def __init__(self, *args, **kwargs):
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
        ]
        super(TrackerCompanySimpleProjectListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_projects()
        return super(TrackerCompanySimpleProjectListView, self).get_queryset()


class TrackerCompanyInternalProjectListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all internal projects wrt company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = project_serializers.ProjectSerializer

    def __init__(self, *args, **kwargs):
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
            'company', 'referent', 'typology', 'completed', 'shared_project', 'logo'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'is_shared', 'is_in_showroom'
        ]
        super(TrackerCompanyInternalProjectListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_internal_projects()
        return super(TrackerCompanyInternalProjectListView, self).get_queryset()


class TrackerCompanySharedProjectListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all shared projects wrt company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = project_serializers.ProjectSerializer

    def __init__(self, *args, **kwargs):
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
            'company', 'referent', 'typology', 'completed'
        ]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn']
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'is_shared', 'is_in_showroom']
        super(TrackerCompanySharedProjectListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_shared_projects()
        return super(TrackerCompanySharedProjectListView, self).get_queryset()


class TrackerCompanyInternalGanttListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all internal tasks wrt company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = project_serializers.TaskSerializer

    def __init__(self, *args, **kwargs):
        self.task_response_include_fields = [
            'id', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'workers', 'progress'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'is_shared', 'is_in_showroom'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'logo'
        ]
        super(TrackerCompanyInternalGanttListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = profile.all_internal_tasks()
            return super(TrackerCompanyInternalGanttListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerCompanySharedGanttListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all shared tasks wrt company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = project_serializers.TaskSerializer

    def __init__(self, *args, **kwargs):
        self.task_response_include_fields = [
            'id', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed'
        ]
        self.company_response_include_fields = ['id', 'name', 'logo']
        super(TrackerCompanySharedGanttListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = profile.all_shared_tasks()
            return super(TrackerCompanySharedGanttListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerCompanyFavouriteMixin(
        JWTPayloadMixin):
    """
    Company Favourite Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            favourite = profile.get_favourite(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, favourite)
            return favourite
        except ObjectDoesNotExist as err:
            raise django_api_exception.FavouriteAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerCompanyFavouriteListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company favourites
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.FavouriteSerializer

    def __init__(self, *args, **kwargs):
        self.favourite_response_include_fields = ['id', 'company_followed', 'company']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn', 'is_supplier', 'logo',
                                                'url', 'email', 'phone', 'phone2', 'fax']
        super(TrackerCompanyFavouriteListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_favourites()
        return super(TrackerCompanyFavouriteListView, self).get_queryset()


class TrackerCompanyFavouriteWaitingListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company favourites
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.FavouriteSerializer

    def __init__(self, *args, **kwargs):
        self.favourite_response_include_fields = ['id', 'company_followed', 'company']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn', 'is_supplier', 'logo',
                                                'url', 'email', 'phone', 'phone2', 'fax']
        super(TrackerCompanyFavouriteWaitingListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_waiting_favourites()
        return super(TrackerCompanyFavouriteWaitingListView, self).get_queryset()


class TrackerCompanyFavouriteReceivedListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company favourites
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.FavouriteSerializer

    def __init__(self, *args, **kwargs):
        self.favourite_response_include_fields = ['id', 'company_followed', 'company']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn', 'is_supplier', 'logo',
                                                'url', 'email', 'phone', 'phone2', 'fax']
        super(TrackerCompanyFavouriteReceivedListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_received_favourites()
        return super(TrackerCompanyFavouriteReceivedListView, self).get_queryset()


class TrackerCompanyNotFavouriteListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company favourites
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.CompanySerializer

    def __init__(self, *args, **kwargs):
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn', 'is_supplier', 'logo']
        super(TrackerCompanyNotFavouriteListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = Company.objects.filter(status=1).exclude(
            id=profile.company.id
         ).exclude(
            request_favourites__company__id=profile.company.id,
            request_favourites__approval_date__isnull=False)
        return super(TrackerCompanyNotFavouriteListView, self).get_queryset()


class TrackerCompanyFavouriteContactListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all public profiles for favourite companies
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'mobile',
            'language', 'fax', 'company', 'user', 'role', 'position',
            'status', 'uidb36', 'token', 'photo', 'company_invitation_date',
            'profile_invitation_date', 'invitation_refuse_date', 'is_shared', 'is_in_showroom'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn', 'logo', 'is_supplier'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(TrackerCompanyFavouriteContactListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        filters = self.get_filters()
        excludes = self.get_excludes()
        order_by = self.get_order_by()
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        public_contacts = profile.list_favourites_public_contact()
        owners = profile.list_favourites_owners()
        if filters:
            if isinstance(filters, dict):
                public_contacts = public_contacts.filter(**filters)
                owners = owners.filter(**filters)
            else:
                public_contacts = public_contacts.filter(filters)
                owners = owners.filter(filters)
        if excludes:
            public_contacts = public_contacts.exclude(**excludes)
            owners = owners.exclude(**excludes)
        if order_by:
            public_contacts = public_contacts.order_by(*order_by)
            owners = owners.order_by(*order_by)
        return public_contacts.union(owners).distinct()


class TrackerCompanyFavouriteDetailView(
        TrackerCompanyFavouriteMixin,
        generics.RetrieveAPIView):
    """
    Get a single favourite
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.CompanySerializer

    def __init__(self, *args, **kwargs):
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn']
        super(TrackerCompanyFavouriteDetailView, self).__init__(*args, **kwargs)


class TrackerCompanyFavouriteDeleteView(
        TrackerCompanyFavouriteMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a single favourite
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.CompanySerializer

    def __init__(self, *args, **kwargs):
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'ssn']
        super(TrackerCompanyFavouriteDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_favourite(instance)


class TrackerCompanyProjectIntervalDetailView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get a company project gantt
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = project_serializers.ProjectCalendarSerializer

    def __init__(self, *args, **kwargs):
        self.project_response_include_fields = [
            'id', 'title', 'start', 'end'
        ]
        super(TrackerCompanyProjectIntervalDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = profile.all_company_projects_interval(
                month=self.kwargs.get('month'), year=self.kwargs.get('year')
            ).order_by('date_start', 'date_end', 'id')
            return super(TrackerCompanyProjectIntervalDetailView, self).get_queryset()

        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProfileProjectIntervalDetailView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get a company project gantt
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = project_serializers.ProjectSerializer

    def __init__(self, *args, **kwargs):
        self.project_response_include_fields = [
            'id', 'name', 'company', 'note', 'days_for_gantt', 'project_owner'
        ]
        self.task_response_include_fields = [
            'id', 'name', 'date_start', 'date_end', 'date_completed'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'logo'
        ]
        super(TrackerProfileProjectIntervalDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

            self.queryset = profile.all_projects_interval(
                month=self.kwargs.get('month'), year=self.kwargs.get('year')
            ).order_by('date_start', 'date_end', 'id')
            return super(TrackerProfileProjectIntervalDetailView, self).get_queryset()

        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProfileActivityIntervalDetailView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get a company profile gantt
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = project_serializers.TaskActivitySerializer

    def __init__(self, *args, **kwargs):
        self.activity_response_include_fields = [
            'task', 'days_for_gantt', 'title', 'alert'
        ]
        self.task_response_include_fields = [
            'project'
        ]
        self.project_response_include_fields = [
            'name'
        ]
        super(TrackerProfileActivityIntervalDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = profile.all_activities_interval(
                month=self.kwargs.get('month'), year=self.kwargs.get('year')
            ).order_by('datetime_start', 'datetime_end', 'id')
            return super(TrackerProfileActivityIntervalDetailView, self).get_queryset()

        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerCompanyStaffActivityIntervalDetailView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get a company profile gantt
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = profile_serializers.ProfileActivitySerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'company', 'days_for_gantt'
        ]
        self.company_response_include_fields = [
            'name', 'logo'
        ]
        super(TrackerCompanyStaffActivityIntervalDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = profile.all_company_staff_interval(
                month=self.kwargs.get('month'), year=self.kwargs.get('year')
            )
            return super(TrackerCompanyStaffActivityIntervalDetailView, self).get_queryset()

        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProfileMessageListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
        Get all project messages
        """
    serializer_class = message_serializers.MessageSerializer

    def __init__(self, *args, **kwargs):
        self.message_response_include_fields = [
            'id', 'body', 'sender', 'date_create', 'unique_code'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'is_shared', 'is_in_showroom'
        ]
        super(TrackerProfileMessageListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_profile_messages()
        return super(TrackerProfileMessageListView, self).get_queryset()


class TrackerProfileToProfileMessageListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
        Get all project messages
        """
    serializer_class = message_serializers.MessageSerializer

    def __init__(self, *args, **kwargs):
        self.message_response_include_fields = [
            'id', 'body', 'sender', 'date_create', 'unique_code'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'is_shared', 'is_in_showroom'
        ]
        super(TrackerProfileToProfileMessageListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        talks = profile.list_profile_to_profile_talks().filter(
            Q(object_id=self.kwargs['profile']) | Q(messages__sender_id=self.kwargs['profile'])
        )
        if talks:
            self.queryset = talks[0].messages.all()
        else:
            self.queryset = talks
        return super(TrackerProfileToProfileMessageListView, self).get_queryset()


class TrackerSponsorMixin(
        JWTPayloadMixin):
    """
    Sponsor Mixin
    """

    def get_profile(self):
        payload = self.get_payload()
        return self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.SponsorSerializer
        else:
            self.serializer_class = output_serializer

    def check_superuser_permissions(self, request, main_profile):
        if not main_profile.is_superuser:
            raise exceptions.PermissionDenied(detail="You don't have privileges for this operation")

    def get_object(self):
        try:
            profile = self.get_profile()
            main_profile = profile.get_main_profile()
            self.check_superuser_permissions(self.request, main_profile)
            sponsor = main_profile.get_sponsor(self.kwargs.get('pk', None))
            return sponsor
        except ObjectDoesNotExist as err:
            raise django_api_exception.NotificationAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerSponsorAddView(
        WhistleGenericViewMixin,
        TrackerSponsorMixin,
        QuerysetMixin,
        generics.CreateAPIView):
    """
        Create sponsor request
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.SponsorAddSerializer

    def __init__(self, *args, **kwargs):
        self.sponsor_request_include_fields = ['short_description']
        self.sponsor_response_include_fields = [
            'id', 'company', 'short_description'
        ]
        self.company_response_include_fields = [
            'id', 'name',
        ]
        super(TrackerSponsorAddView, self).__init__(*args, **kwargs)


class TrackerSponsorListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
        Get all project messages
        """
    serializer_class = serializers.SponsorSerializer

    def __init__(self, *args, **kwargs):
        self.sponsor_response_include_fields = [
            'id', 'company', 'status', 'short_description', 'tags', 'categories', 'expired_date'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'logo'
        ]
        super(TrackerSponsorListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        main_profile = profile.get_main_profile()
        if main_profile.is_superuser:
            self.queryset = models.Sponsor.objects.all()
        else:
            self.queryset = profile.get_sponsor_list()
        return super(TrackerSponsorListView, self).get_queryset()


class TrackerCompanySponsorActiveListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
        Get all project messages
        """
    serializer_class = serializers.SponsorSerializer

    def __init__(self, *args, **kwargs):
        self.sponsor_response_include_fields = [
            'id', 'company', 'status', 'short_description', 'tags', 'categories'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'logo', 'category'
        ]
        super(TrackerCompanySponsorActiveListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.get_active_sponsor_list()
        return super(TrackerCompanySponsorActiveListView, self).get_queryset()


class TrackerSponsorDetailView(
        TrackerSponsorMixin,
        QuerysetMixin,
        generics.RetrieveAPIView):
    """
    Get a single sponsor
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.SponsorSerializer

    def __init__(self, *args, **kwargs):
        self.sponsor_response_include_fields = [
            'id', 'company', 'status', 'short_description', 'tags', 'expired_date'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'logo'
        ]
        super(TrackerSponsorDetailView, self).__init__(*args, **kwargs)


class TrackerSponsorEditView(
        WhistleGenericViewMixin,
        TrackerSponsorMixin,
        generics.RetrieveUpdateAPIView):
    """
    Update a single company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.SponsorEditSerializer

    def __init__(self, *args, **kwargs):
        self.sponsor_request_include_fields = [
            'id', 'company', 'short_description', 'status', 'tags', 'expired_date'
        ]
        self.sponsor_response_include_fields = [
            'id', 'company', 'short_description', 'status', 'tags', 'expired_date'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'logo'
        ]
        super(TrackerSponsorEditView, self).__init__(*args, **kwargs)

    def put(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True
        if 'tags' in request.data:
            tags_field = {}
            if isinstance(request.data['tags'], str):
                category_list = request.data['tags'].split(',')
                qs = Category.objects.filter(code__in=category_list)
                for row in qs:
                    tags_field[row.code] = {'name': row.name, 'color': row.typology.color}
                request.data['tags'] = json.dumps(tags_field)
            else:
                qs = Category.objects.filter(code__in=request.data['tags'])
                for row in qs:
                    tags_field[row.code] = {'name': row.name, 'color': row.typology.color}
                request.data['tags'] = tags_field
        return super(TrackerSponsorEditView, self).put(request, *args, **kwargs)

