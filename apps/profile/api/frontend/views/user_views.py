# -*- coding: utf-8 -*-
import json
import operator
import random
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

palette_color = [
    '#d32f2f',
    '#7b1fa2',
    '#303f9f',
    '#00796b',
    '#00e5ff',
    '#1b5e20',
    '#76ff03',
    '#ffeb3b',
    '#ff6f00',
    '#795548',
    '#212121',
    '#ff4081',
]
palette_color2 = [
'#F44336',
  '#FFEBEE',
  '#FFCDD2',
  '#EF9A9A',
  '#E57373',
  '#EF5350',
  '#F44336',
  '#E53935',
  '#D32F2F',
  '#C62828',
  '#B71C1C',
  '#FF8A80',
  '#FF5252',
  '#FF1744',
  '#D50000',
  '#E91E63',
  '#FCE4EC',
  '#F8BBD0',
  '#F48FB1',
  '#F06292',
  '#EC407A',
  '#E91E63',
  '#D81B60',
  '#C2185B',
  '#AD1457',
  '#880E4F',
  '#FF80AB',
  '#FF4081',
  '#F50057',
  '#C51162',
  '#9C27B0',
  '#F3E5F5',
  '#E1BEE7',
  '#CE93D8',
  '#BA68C8',
  '#AB47BC',
  '#9C27B0',
  '#8E24AA',
  '#7B1FA2',
  '#6A1B9A',
  '#4A148C',
  '#EA80FC',
  '#E040FB',
  '#D500F9',
  '#AA00FF',
  '#673AB7',
  '#EDE7F6',
  '#D1C4E9',
  '#B39DDB',
  '#9575CD',
  '#7E57C2',
  '#673AB7',
  '#5E35B1',
  '#512DA8',
  '#4527A0',
  '#311B92',
  '#B388FF',
  '#7C4DFF',
  '#651FFF',
  '#6200EA',
  '#3F51B5',
  '#E8EAF6',
  '#C5CAE9',
  '#9FA8DA',
  '#7986CB',
  '#5C6BC0',
  '#3F51B5',
  '#3949AB',
  '#303F9F',
  '#283593',
  '#1A237E',
  '#8C9EFF',
  '#536DFE',
  '#3D5AFE',
  '#304FFE',
  '#2196F3',
  '#E3F2FD',
  '#BBDEFB',
  '#90CAF9',
  '#64B5F6',
  '#42A5F5',
  '#2196F3',
  '#1E88E5',
  '#1976D2',
  '#1565C0',
  '#0D47A1',
  '#82B1FF',
  '#448AFF',
  '#2979FF',
  '#2962FF',
  '#03A9F4',
  '#E1F5FE',
  '#B3E5FC',
  '#81D4FA',
  '#4FC3F7',
  '#29B6F6',
  '#03A9F4',
  '#039BE5',
  '#0288D1',
  '#0277BD',
  '#01579B',
  '#80D8FF',
  '#40C4FF',
  '#00B0FF',
  '#0091EA',
  '#00BCD4',
  '#E0F7FA',
  '#B2EBF2',
  '#80DEEA',
  '#4DD0E1',
  '#26C6DA',
  '#00BCD4',
  '#00ACC1',
  '#0097A7',
  '#00838F',
  '#006064',
  '#84FFFF',
  '#18FFFF',
  '#00E5FF',
  '#00B8D4',
  '#009688',
  '#E0F2F1',
  '#B2DFDB',
  '#80CBC4',
  '#4DB6AC',
  '#26A69A',
  '#009688',
  '#00897B',
  '#00796B',
  '#00695C',
  '#004D40',
  '#A7FFEB',
  '#64FFDA',
  '#1DE9B6',
  '#00BFA5',
  '#4CAF50',
  '#E8F5E9',
  '#C8E6C9',
  '#A5D6A7',
  '#81C784',
  '#66BB6A',
  '#4CAF50',
  '#43A047',
  '#388E3C',
  '#2E7D32',
  '#1B5E20',
  '#B9F6CA',
  '#69F0AE',
  '#00E676',
  '#00C853',
  '#8BC34A',
  '#F1F8E9',
  '#DCEDC8',
  '#C5E1A5',
  '#AED581',
  '#9CCC65',
  '#8BC34A',
  '#7CB342',
  '#689F38',
  '#558B2F',
  '#33691E',
  '#CCFF90',
  '#B2FF59',
  '#76FF03',
  '#64DD17',
  '#CDDC39',
  '#F9FBE7',
  '#F0F4C3',
  '#E6EE9C',
  '#DCE775',
  '#D4E157',
  '#CDDC39',
  '#C0CA33',
  '#AFB42B',
  '#9E9D24',
  '#827717',
  '#F4FF81',
  '#EEFF41',
  '#C6FF00',
  '#AEEA00',
  '#FFEB3B',
  '#FFFDE7',
  '#FFF9C4',
  '#FFF59D',
  '#FFF176',
  '#FFEE58',
  '#FFEB3B',
  '#FDD835',
  '#FBC02D',
  '#F9A825',
  '#F57F17',
  '#FFFF8D',
  '#FFFF00',
  '#FFEA00',
  '#FFD600',
  '#FFC107',
  '#FFF8E1',
  '#FFECB3',
  '#FFE082',
  '#FFD54F',
  '#FFCA28',
  '#FFC107',
  '#FFB300',
  '#FFA000',
  '#FF8F00',
  '#FF6F00',
  '#FFE57F',
  '#FFD740',
  '#FFC400',
  '#FFAB00',
  '#FF9800',
  '#FFF3E0',
  '#FFE0B2',
  '#FFCC80',
  '#FFB74D',
  '#FFA726',
  '#FF9800',
  '#FB8C00',
  '#F57C00',
  '#EF6C00',
  '#E65100',
  '#FFD180',
  '#FFAB40',
  '#FF9100',
  '#FF6D00',
  '#FF5722',
  '#FBE9E7',
  '#FFCCBC',
  '#FFAB91',
  '#FF8A65',
  '#FF7043',
  '#FF5722',
  '#F4511E',
  '#E64A19',
  '#D84315',
  '#BF360C',
  '#FF9E80',
  '#FF6E40',
  '#FF3D00',
  '#DD2C00',
  '#795548',
  '#EFEBE9',
  '#D7CCC8',
  '#BCAAA4',
  '#A1887F',
  '#8D6E63',
  '#795548',
  '#6D4C41',
  '#5D4037',
  '#4E342E',
  '#3E2723',
  '#9E9E9E',
  '#FAFAFA',
  '#F5F5F5',
  '#EEEEEE',
  '#E0E0E0',
  '#BDBDBD',
  '#9E9E9E',
  '#757575',
  '#616161',
  '#424242',
  '#212121',
  '#607D8B',
  '#ECEFF1',
  '#CFD8DC',
  '#B0BEC5',
  '#90A4AE',
  '#78909C',
  '#607D8B',
  '#546E7A',
  '#455A64',
  '#37474F',
  '#263238',
  '#000000',
  '#FFFFFF',
]

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
            'name', 'slug', 'brand', 'tax_code', 'vat_number',
            'url', 'email', 'phone', 'phone2', 'fax', 'logo',
            'note', 'category', 'description', 'is_supplier', 'color'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'brand', 'tax_code', 'vat_number',
            'url', 'email', 'phone', 'phone2', 'fax', 'logo',
            'note', 'category', 'color'
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
        request.data['color'] = random.choice(palette_color)
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
            'id', 'name', 'slug', 'email', 'tax_code',
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
            'id', 'name', 'slug', 'email', 'tax_code',
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
            'id', 'name', 'slug', 'email', 'tax_code',
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
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
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
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
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
            'fax', 'mobile', 'note', 'photo', 'can_access_chat', 'can_access_files'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'email',
            'company_invitation_date', 'profile_invitation_date',
            'invitation_refuse_date', 'phone', 'language',
            'position', 'role', 'status', 'photo', 'fax', 'mobile', 'note',
            'can_access_chat', 'can_access_files', 'is_invited'
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
            'uidb36', 'token', 'is_superuser', 'can_access_files', 'can_access_chat'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'url',
            'tax_code', 'logo', 'creator', 'color', 'vat_number', 'description',
            'fax', 'phone', 'phone2', 'customer', 'trial_used', 'subscription'
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
            'tax_code', 'logo'
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
            'tax_code', 'logo'
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
    permission_classes = ()
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
            'tax_code', 'logo'
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
