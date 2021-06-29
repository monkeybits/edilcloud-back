# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions

from apps.media.api.frontend import serializers as media_serializers
from apps.quotation.api.frontend import serializers as quotation_serializers
from web.api.views import QuerysetMixin
from apps.profile.api.frontend import serializers
from apps.profile import models


class CompanyListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all companies
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.CompanySerializer

    def __init__(self, *args, **kwargs):
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'url', 'email', 'phone',
            'logo', 'followed', 'is_supplier','country', 'address',
            'sdi', 'province', 'cap', 'tax_code', 
            'vat_number', 'pec', 'billing_email'
        ]
        super(CompanyListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        self.queryset = models.Company.objects.active()
        return super(CompanyListView, self).get_queryset().filter()


class CompanyDetailView(
        generics.RetrieveAPIView):
    """
    Get a single company
    """
    permission_classes = (permissions.AllowAny,)
    queryset = models.Company.objects.active()
    serializer_class = serializers.CompanySerializer

    def __init__(self, *args, **kwargs):
        self.company_response_include_fields = [
            'id', 'name', 'brand', 'description', 'slug', 'email', 'tax_code',
            'email', 'phone', 'logo', 'vat_number',
            'url', 'fax', 'phone2', 'projects_count',
            'messages_count', 'tags_count', 'followers_count',
            'staff_count', 'partnerships_count', 'category',
            'address', 'province', 'cap', 'country', 'pec',
            'billing_email', 'customer', 'trial_used', 'subscription'
        ]
        super(CompanyDetailView, self).__init__(*args, **kwargs)


class CompanyPhotoListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company photos
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = media_serializers.PhotoSerializer

    def __init__(self, *args, **kwargs):
        self.photo_response_include_fields = ['id', 'title', 'pub_date', 'photo', 'extension',
            'photo_64', 'note', 'tags', 'relative_path', 'folder_relative_path']
        super(CompanyPhotoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.get_photos()
        return super(CompanyPhotoListView, self).get_queryset()


class CompanyPublicPhotoListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company photos
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = media_serializers.PhotoSerializer

    def __init__(self, *args, **kwargs):
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo', 'extension',
            'photo_64', 'note', 'is_public'
        ]
        super(CompanyPublicPhotoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.list_public_company_photos()
        return super(CompanyPublicPhotoListView, self).get_queryset()


class CompanyVideoListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company videos
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = media_serializers.VideoSerializer

    def __init__(self, *args, **kwargs):
        self.video_response_include_fields = ['id', 'title', 'pub_date', 'video', 'extension']
        super(CompanyVideoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.get_videos()
        return super(CompanyVideoListView, self).get_queryset()


class CompanyPublicVideoListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company Videos
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = media_serializers.VideoSerializer

    def __init__(self, *args, **kwargs):
        self.video_response_include_fields = [
            'id', 'title', 'pub_date', 'video',
            'extension', 'note', 'is_public'
        ]
        super(CompanyPublicVideoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.list_public_company_videos()
        return super(CompanyPublicVideoListView, self).get_queryset()


class CompanyOfferListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company offers
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = quotation_serializers.OfferSerializer

    def __init__(self, *args, **kwargs):
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date',
            'deadline', 'price', 'contact', 'owner', 'tags'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name',
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code'
        ]
        super(CompanyOfferListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.get_active_offers()
        return super(CompanyOfferListView, self).get_queryset()


class CompanyActiveOfferListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company offers
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = quotation_serializers.OfferSerializer

    def __init__(self, *args, **kwargs):
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date', 'photo', 'followers', 'buyers',
            'deadline', 'price', 'contact', 'owner', 'tags', 'start_date'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name',
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code'
        ]
        super(CompanyActiveOfferListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.get_active_offers().filter(is_draft=False)
        return super(CompanyActiveOfferListView, self).get_queryset()


class CompanyPartnerShipList(
        QuerysetMixin,
        generics.ListAPIView):
    """
        Get all partnership
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.PartnershipSerializer

    def __init__(self, *args, **kwargs):
        self.partnership_response_include_fields = [
            'id', 'inviting_company', 'guest_company',
            'invitation_date', 'approval_date'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'logo'
        ]
        super(CompanyPartnerShipList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.list_partnerships()
        return super(CompanyPartnerShipList, self).get_queryset()


class CompanyCertificationListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company certificates
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = quotation_serializers.CertificationSerializer

    def __init__(self, *args, **kwargs):
        self.certification_response_include_fields = ['id', 'title', 'description', 'document', 'contact', 'owner',]
        self.profile_response_include_fields = ['id', 'first_name', 'last_name',]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        super(CompanyCertificationListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.get_certifications()
        return super(CompanyCertificationListView, self).get_queryset()


class CompanyStaffListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company staffs
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user', 'can_access_files', 'can_access_chat']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(CompanyStaffListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.get_active_staff()
        return super(CompanyStaffListView, self).get_queryset()


class CompanyPublicStaffListView(
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all company owners list
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user', 'phone', 'mobile',
                                                'email', 'language', 'role', 'is_shared', 'is_in_showroom', 'photo']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code', 'is_supplier']

        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(CompanyPublicStaffListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.get_active_public_staff()
        return super(CompanyPublicStaffListView, self).get_queryset()


class CompanyShowroomContactListView(
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all company owners list
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user', 'phone', 'mobile',
                                                'email', 'language', 'role', 'is_shared', 'is_in_showroom', 'photo']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']

        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(CompanyShowroomContactListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.get_active_showroom_staff()
        return super(CompanyShowroomContactListView, self).get_queryset()


class CompanyContactListView(
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all company owners list
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user', 'phone', 'mobile',
                                                'email', 'language', 'role', 'is_shared', 'photo', 'is_in_showroom']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']

        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(CompanyContactListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.list_contacts()
        return super(CompanyContactListView, self).get_queryset()


class CompanyOwnerListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company owners
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(CompanyOwnerListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.get_owners()
        return super(CompanyOwnerListView, self).get_queryset()


class CompanyDelegateListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company delegate members
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(CompanyDelegateListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.get_delegates()
        return super(CompanyDelegateListView, self).get_queryset()


class CompanyLevel1ListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company level1 team members
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(CompanyLevel1ListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.get_managers()
        return super(CompanyLevel1ListView, self).get_queryset()


class CompanyLevel2ListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company level2 team members
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'company', 'user']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        self.user_response_include_fields = ['id', 'first_name', 'last_name']
        super(CompanyLevel2ListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        company = get_object_or_404(
            models.Company.objects.active().filter(id=self.kwargs.get('pk', None))
        )
        self.queryset = company.get_workers()
        return super(CompanyLevel2ListView, self).get_queryset()


class ProfileDetailView(
        generics.RetrieveAPIView):
    """
    Get a single profile
    """
    permission_classes = (permissions.AllowAny,)
    queryset = models.Profile.objects.active()
    serializer_class = serializers.ProfileSerializer

    def __init__(self, *args, **kwargs):
        self.profile_response_include_fields = ['id', 'first_name', 'last_name', 'language', 'position', 'role',
                                                'email', 'phone', 'fax', 'mobile', 'note', 'photo',
                                                'company_invitation_date', 'profile_invitation_date',
                                                'invitation_refuse_date']
        super(ProfileDetailView, self).__init__(*args, **kwargs)
