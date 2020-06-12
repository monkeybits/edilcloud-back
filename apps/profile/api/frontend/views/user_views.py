# -*- coding: utf-8 -*-
import json
import operator
from functools import reduce

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from rest_framework import generics, status

from apps.product.models import Category
from web.api.permissions import IsAuthenticatedAndOwnerPermission
from web.api.views import QuerysetMixin
from apps.profile.api.frontend import serializers
from apps.profile import models
from web.drf import exceptions as django_api_exception
from web import exceptions as django_exception
from web.api.views import WhistleGenericViewMixin, JWTPayloadMixin


class UserProfileMixin(
        JWTPayloadMixin):
    """
    Profile Mixin
    """
    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.ProfileSerializer
        else:
            self.serializer_class = output_serializer


class UserCompanyMixin(
        JWTPayloadMixin):
    """
    Company Mixin
    """
    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.CompanySerializer
        else:
            self.serializer_class = output_serializer


class CompanyAddView(
        WhistleGenericViewMixin,
        UserCompanyMixin,
        generics.CreateAPIView):
    """
    Creates a company and then company profile
    """
    serializer_class = serializers.CompanyAddSerializer

    def __init__(self, *args, **kwargs):
        self.company_request_include_fields = [
            'name', 'slug', 'brand', 'ssn', 'vat_number',
            'url', 'email', 'phone', 'phone2', 'fax', 'logo',
            'note', 'category', 'description', 'is_supplier'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'brand', 'ssn', 'vat_number',
            'url', 'email', 'phone', 'phone2', 'fax', 'logo',
            'note', 'category'
        ]
        super(CompanyAddView, self).__init__(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True
        if 'category' in request.data:
            category_field = {}
            if isinstance(request.data['category'], str):
                category_list = request.data['category'].split(',')
                qs = Category.objects.filter(code__in=category_list)
            else:
                qs = Category.objects.filter(code__in=request.data['category'])
            for row in qs:
                category_field[row.code] = row.name
            request.data['category'] = json.dumps(category_field)
        return super(CompanyAddView, self).post(request, *args, **kwargs)


class MyCompanyListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all companies connected to their user
    """

    serializer_class = serializers.CompanySerializer

    def __init__(self, *args, **kwargs):
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn',
            'email', 'phone', 'logo'
        ]
        super(MyCompanyListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            main_profile = self.request.user.get_main_profile()
            self.queryset = main_profile.list_companies()
            return super(MyCompanyListView, self).get_queryset()
        except django_exception.MainProfileDoesNotExist as err:
            raise django_api_exception.MainProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _(err.msg)
            )
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err))
            )


class MyCompanyActiveListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all active companies w.r.t. user
    """
    serializer_class = serializers.CompanySerializer

    def __init__(self, *args, **kwargs):
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn',
            'email', 'phone', 'logo'
        ]
        super(MyCompanyActiveListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            main_profile = self.request.user.get_main_profile()
            self.queryset = main_profile.get_active_companies()
            return super(MyCompanyActiveListView, self).get_queryset()
        except django_exception.MainProfileDoesNotExist as err:
            raise django_api_exception.MainProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _(err.msg)
            )
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err))
            )


class MyCompanyInactiveListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all inactive companies w.r.t. user
    """
    serializer_class = serializers.CompanySerializer

    def __init__(self, *args, **kwargs):
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn',
            'email', 'phone', 'logo'
        ]
        super(MyCompanyInactiveListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            main_profile = self.request.user.get_main_profile()
            self.queryset = main_profile.get_inactive_companies()
            return super(MyCompanyInactiveListView, self).get_queryset()
        except django_exception.MainProfileDoesNotExist as err:
            raise django_api_exception.MainProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _(err.msg)
            )
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err))
            )


class ProfileActiveListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all MainProfiles of Whistle active
    """
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'company', 'user', 'photo'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn', 'logo'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(ProfileActiveListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            main_profile = self.request.user.get_main_profile()
            self.queryset = main_profile.list_mains()
            return super(ProfileActiveListView, self).get_queryset()
        except django_exception.MainProfileDoesNotExist as err:
            raise django_api_exception.MainProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _(err.msg)
            )
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err))
            )


class ProfilesActiveListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all MainProfiles of Whistle active
    """
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'role', 'position',
            'company', 'photo', 'email', 'language'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'ssn', 'logo'
        ]
        super(ProfilesActiveListView, self).__init__(*args, **kwargs)
        
    def get_filters(self):
        filters = super(ProfilesActiveListView, self).get_filters()
        if filters:
            if len(filters) != 1:
                query = []
                for key, value in enumerate(filters):
                    query.append(tuple((value, filters[value])))
                return reduce(operator.or_, [Q(x) for x in query])
        return filters

    def get_queryset(self):
        try:
            self.queryset = self.request.user.get_all_profiles()
            return super(ProfilesActiveListView, self).get_queryset()
        except django_exception.MainProfileDoesNotExist as err:
            raise django_api_exception.MainProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _(err.msg)
            )
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err))
            )


class ProfileAddView(
        WhistleGenericViewMixin,
        UserProfileMixin,
        generics.CreateAPIView):
    """
    Create a main profile
    """
    serializer_class = serializers.MainProfileAddSerializer

    def __init__(self, *args, **kwargs):
        self.profile_request_include_fields = [
            'first_name', 'last_name', 'email',
            'language', 'position', 'user', 'phone',
            'fax', 'mobile', 'note', 'photo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email',
            'company_invitation_date', 'profile_invitation_date',
            'invitation_refuse_date', 'phone', 'language',
            'position', 'role', 'status', 'photo', 'fax', 'mobile', 'note',
        ]
        super(ProfileAddView, self).__init__(*args, **kwargs)


class ProfileListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all profiles w.r.t. user
    """
    permission_classes = (IsAuthenticatedAndOwnerPermission,)
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'company', 'user',
            'email', 'company_invitation_date', 'profile_invitation_date',
            'invitation_refuse_date', 'phone', 'language',
            'position', 'role', 'status', 'photo', 'fax', 'mobile', 'note', 'is_main',
            'uidb36', 'token', 'is_superuser'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'url',
            'ssn', 'logo', 'creator'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(ProfileListView, self).__init__(*args, **kwargs)

    def change_queryset_ordering(self):
        payload = self.get_payload()
        if payload['extra']:
            selected_profile = [payload['extra']['profile']['id']]
            remaining_profiles = list(self.queryset.exclude(id=payload['extra']['profile']['id']).values_list('id', flat=True))
            # Todo: improve the querysets merge (It seems, Union doesnt work for ordering)
            pk_list = selected_profile + remaining_profiles
            clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(pk_list)])
            ordering = 'CASE %s END' % clauses
            self.queryset = self.queryset.extra(select={'order': ordering}, order_by=('order',))
        return self.queryset

    def get_queryset(self):
        generic = 'get_'+self.kwargs.get('type')+'_profiles'
        self.queryset = getattr(self.request.user, generic)()
        if not self.get_filters() and not self.get_excludes() and not self.get_order_by():
            self.change_queryset_ordering()
        return super(ProfileListView, self).get_queryset()


class ProfileAcceptListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all profiles w.r.t. user
    """
    permission_classes = (IsAuthenticatedAndOwnerPermission,)
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'company', 'user',
            'email', 'company_invitation_date', 'profile_invitation_date',
            'invitation_refuse_date', 'phone', 'language',
            'position', 'role', 'status', 'photo', 'fax', 'mobile', 'note', 'is_main',
            'uidb36', 'token'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'url',
            'ssn', 'logo'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(ProfileAcceptListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        self.queryset = self.request.user.get_approve_profiles()
        return super(ProfileAcceptListView, self).get_queryset()


class ProfileRefuseListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all profiles w.r.t. user
    """
    permission_classes = (IsAuthenticatedAndOwnerPermission,)
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'company', 'user',
            'email', 'company_invitation_date', 'profile_invitation_date',
            'invitation_refuse_date', 'phone', 'language',
            'position', 'role', 'status', 'photo', 'fax', 'mobile', 'note', 'is_main',
            'uidb36', 'token'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'url',
            'ssn', 'logo'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(ProfileRefuseListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        self.queryset = self.request.user.get_refuse_profiles()
        return super(ProfileRefuseListView, self).get_queryset()


class ProfileEditView(
        WhistleGenericViewMixin,
        UserProfileMixin,
        generics.RetrieveUpdateAPIView):
    """
    Update a main profile
    PS: This is only for main profile
    """
    permission_classes = (IsAuthenticatedAndOwnerPermission,)
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileEditSerializer

    def __init__(self, *args, **kwargs):
        self.profile_request_include_fields = [
            'first_name', 'last_name', 'email',
            'language', 'position', 'user', 'phone',
            'fax', 'mobile', 'note', 'photo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name',
            'email', 'company_invitation_date', 'profile_invitation_date',
            'invitation_refuse_date', 'phone', 'language',
            'position', 'role', 'status', 'photo', 'fax', 'mobile', 'note',
        ]

        super(ProfileEditView, self).__init__(*args, **kwargs)


class ProfileEnableView(
        WhistleGenericViewMixin,
        UserProfileMixin,
        generics.RetrieveUpdateAPIView):
    """
    Enable a main profile
    PS: This is only for main profile
    """
    permission_classes = (IsAuthenticatedAndOwnerPermission,)
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileEnableSerializer

    def __init__(self, *args, **kwargs):
        self.profile_request_include_fields = []
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email',
            'language', 'position', 'photo', 'status'
        ]
        super(ProfileEnableView, self).__init__(*args, **kwargs)


class ProfileDisableView(
        WhistleGenericViewMixin,
        UserProfileMixin,
        generics.RetrieveUpdateAPIView):
    """
    Disable a main profile
    PS: This is only for main profile
    """
    permission_classes = (IsAuthenticatedAndOwnerPermission,)
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileDisableSerializer

    def __init__(self, *args, **kwargs):
        self.profile_request_include_fields = []
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email',
            'language', 'position', 'photo', 'status'
        ]
        super(ProfileDisableView, self).__init__(*args, **kwargs)


class ProfileDeleteView(
        WhistleGenericViewMixin,
        UserProfileMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a main profile
    PS: This is only for main profile
    """
    permission_classes = (IsAuthenticatedAndOwnerPermission,)
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileEditSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email',
            'language', 'position', 'photo'
        ]
        super(ProfileDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        try:
            main_profile = self.request.user.get_main_profile()
            main_profile.remove_profile(instance)
        except django_exception.MainProfileDoesNotExist as err:
            raise django_api_exception.MainProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _(err.msg)
            )
        except Exception as err:
            raise django_api_exception.WhistleAPIException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, self.request, _("{}".format(err))
            )


class ProfileSendInviteView(
        WhistleGenericViewMixin,
        UserProfileMixin,
        generics.CreateAPIView):
    """
    Create profile invite request to a company
    """
    queryset = models.Company.objects.all()
    serializer_class = serializers.ProfileInvitationAddSerializer

    def __init__(self, *args, **kwargs):
        self.profile_request_include_fields = [
            'company', 'user'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'company', 'user',
            'email', 'company_invitation_date', 'profile_invitation_date',
            'invitation_refuse_date', 'phone', 'language',
            'position', 'role', 'status', 'photo', 'fax', 'mobile', 'note', 'is_main'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'url',
            'ssn', 'logo'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(ProfileSendInviteView, self).__init__(*args, **kwargs)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {'pk': self.kwargs.get('company_pk', None)}
        return get_object_or_404(queryset, **filter_kwargs)

    def post(self, request, *args, **kwargs):
        company = self.get_object()
        if not request.POST._mutable:
            request.POST._mutable = True

        request.data['company'] = company.id
        request.data['user'] = request.user.id
        return self.create(request, *args, **kwargs)
