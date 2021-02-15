# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.serializers import json
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import generics, status
from rest_framework.response import Response

from apps.document.api.frontend import serializers as document_serializers
from apps.profile.models import Company
from apps.project.api.frontend import serializers as project_serializers
from apps.media.api.frontend import serializers as media_serializers
from apps.quotation.models import FavouriteOffer, BoughtOffer
from web.api.permissions import RoleAccessPermission
from web.api.views import QuerysetMixin, JWTPayloadMixin, WhistleGenericViewMixin
from apps.quotation.api.frontend import serializers
from web.drf import exceptions as django_api_exception


class TrackerBomMixin(
        JWTPayloadMixin):
    """
    Company Bom Mixin
    """
    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            if 'type' in self.kwargs:
                get_method = 'get_{}_bom'.format(self.kwargs['type'])
                bom = getattr(profile, get_method)(self.kwargs.get('pk', None))
            else:
                bom = profile.get_bom(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, bom['bom'])
            return bom['bom']
        except ObjectDoesNotExist as err:
            raise django_api_exception.BomAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.BomSerializer
        else:
            self.serializer_class = output_serializer


class TrackerBomDetailView(
        TrackerBomMixin,
        QuerysetMixin,
        generics.RetrieveAPIView):
    """
    Get a single company bom
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.BomSerializer

    def __init__(self, *args, **kwargs):
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom', 'deadline', 'project',
            'tags', 'bom_rows', 'selected_companies', 'owner', 'get_bom_rows_count',
            'is_draft'
        ]
        self.bomrow_response_include_fields = [
            'id', 'bom', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.project_response_include_fields = [
            'id', 'name'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]
        super(TrackerBomDetailView, self).__init__(*args, **kwargs)


class TrackerBomBomTypeDetailView(
        TrackerBomMixin,
        QuerysetMixin,
        generics.RetrieveAPIView):
    """
    Get a single company bom
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.BomSerializer

    def __init__(self, *args, **kwargs):
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom', 'deadline', 'project',
            'tags', 'bom_rows', 'selected_companies', 'owner', 'get_bom_rows_count',
            'is_draft'
        ]
        self.bomrow_response_include_fields = [
            'id', 'bom', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.project_response_include_fields = [
            'id', 'name'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]
        super(TrackerBomBomTypeDetailView, self).__init__(*args, **kwargs)
    

class TrackerBomSenderListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company boms
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.BomSerializer

    def __init__(self, *args, **kwargs):
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom', 'deadline',
            'tags', 'bom_rows', 'selected_companies', 'status', 'project'
        ]
        self.bomrow_response_include_fields = [
            'id', 'bom', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity', 'status'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'typology'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]
        super(TrackerBomSenderListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_sent_boms()
        self.queryset = self.queryset.exclude(archived_boms__company=profile.company)
        return super(TrackerBomSenderListView, self).get_queryset().select_related(
            'project',
        ).prefetch_related(
            'selected_companies',
            'bom_rows__typology', 'bom_rows__category', 'bom_rows__subcategory',
            'bom_rows__product', 'bom_rows__unit',
        )


class TrackerBomDraftListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company boms
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.BomSerializer

    def __init__(self, *args, **kwargs):
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom', 'deadline',
            'tags', 'bom_rows', 'selected_companies', 'status', 'project'
        ]
        self.bomrow_response_include_fields = [
            'id', 'bom', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity', 'status'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'typology'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]
        super(TrackerBomDraftListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_draft_boms()
        return super(TrackerBomDraftListView, self).get_queryset().select_related(
            'project',
        ).prefetch_related(
            'selected_companies',
            'bom_rows__typology', 'bom_rows__category', 'bom_rows__subcategory',
            'bom_rows__product', 'bom_rows__unit',
        )


class TrackerBomReceiverListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company boms
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.BomSerializer

    def __init__(self, *args, **kwargs):
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom', 'deadline',
            'tags', 'bom_rows', 'owner', 'status', 'project', 'selected_companies'
        ]
        self.bomrow_response_include_fields = [
            'id', 'bom', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity', 'status'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'typology'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]
        super(TrackerBomReceiverListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_received_boms()
        self.queryset = self.queryset.exclude(archived_boms__company=profile.company)
        return super(TrackerBomReceiverListView, self).get_queryset().select_related(
            'project', 'owner',
        ).prefetch_related(
            'bom_rows__typology', 'bom_rows__category', 'bom_rows__subcategory',
            'bom_rows__product', 'bom_rows__unit',
        )


class TrackerBomAddView(
        WhistleGenericViewMixin,
        TrackerBomMixin,
        generics.CreateAPIView):
    """
    Add a company bom
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.BomAndBomRowAddSerializer

    def __init__(self, *args, **kwargs):
        self.bom_request_include_fields = [
            'title', 'description', 'date_bom',
            'deadline', 'tags', 'project', 'selected_companies'
        ]
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom', 'deadline',
            'tags', 'bom_rows', 'selected_companies', 'project'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'typology'
        ]
        self.bomrow_response_include_fields = [
            'id', 'bom', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        super(TrackerBomAddView, self).__init__(*args, **kwargs)


class TrackerBomEditView(
        WhistleGenericViewMixin,
        TrackerBomMixin,
        generics.RetrieveUpdateAPIView):
    """
    Update a single company bom
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.BomEditSerializer

    def __init__(self, *args, **kwargs):
        self.bom_request_include_fields = [
            'title', 'description', 'date_bom', 'deadline', 'tags',
            'selected_companies', 'is_draft', 'project'
        ]
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom', 'deadline',
            'tags', 'selected_companies', 'project', 'is_draft'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'typology'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        super(TrackerBomEditView, self).__init__(*args, **kwargs)


class TrackerBomPublishView(
        WhistleGenericViewMixin,
        TrackerBomMixin,
        generics.RetrieveUpdateAPIView):
    """
    Update a single company bom
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.BomSendSerializer

    def __init__(self, *args, **kwargs):
        self.bom_request_include_fields = [
            'title', 'description', 'date_bom', 'deadline', 'tags',
            'selected_companies', 'is_draft', 'project'
        ]
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom', 'deadline',
            'tags', 'selected_companies', 'project', 'is_draft'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'typology'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        super(TrackerBomPublishView, self).__init__(*args, **kwargs)

    def put(self, request, *args, **kwargs):
        companies_qs = Company.objects.filter(
            category__has_any_keys=request.data['selected_companies'], is_supplier=True
        ).distinct()
        request.data['selected_companies'] = []
        if not companies_qs:
            return Response({'categories': "No companies for selected categories"}, status=status.HTTP_400_BAD_REQUEST)
        for row in companies_qs:
            request.data['selected_companies'].append(row.id)
        request.data['is_draft'] = False
        return super(TrackerBomPublishView, self).put(request, *args, **kwargs)


class TrackerBomSendView(
        WhistleGenericViewMixin,
        TrackerBomMixin,
        generics.RetrieveUpdateAPIView):
    """
    Update a single company bom
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.BomSendSerializer

    def __init__(self, *args, **kwargs):
        self.bom_request_include_fields = [
            'title', 'description', 'date_bom', 'deadline', 'tags',
            'selected_companies', 'is_draft', 'project'
        ]
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom', 'deadline',
            'tags', 'selected_companies', 'project', 'is_draft'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'typology'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        super(TrackerBomSendView, self).__init__(*args, **kwargs)

    def put(self, request, *args, **kwargs):
        request.data['is_draft'] = False
        return super(TrackerBomSendView, self).put(request, *args, **kwargs)


class TrackerBomDeleteView(
        TrackerBomMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a single company bom
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.BomSerializer

    def __init__(self, *args, **kwargs):
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom', 'deadline',
            'tags', 'selected_companies'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        super(TrackerBomDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_bom(instance)


class TrackerBomBomTypeDocumentListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all sent boms documents
    # Todo: Use managers, if required
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = document_serializers.DocumentSerializer

    def __init__(self, *args, **kwargs):
        self.document_response_include_fields = ['id', 'title', 'description', 'document', 'date_create', 'extension']
        super(TrackerBomBomTypeDocumentListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            list_method = 'list_{}_boms'.format(self.kwargs['type'])
            bom = getattr(profile, list_method)().get(id=self.kwargs.get('pk'))
            qs_method = 'list_{}_bom_documents'.format(self.kwargs['type'])
            self.queryset = getattr(profile, qs_method)(bom=bom)
            return super(TrackerBomBomTypeDocumentListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProjectAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerBomBomTypePhotoListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all sent boms photos
    # Todo: Use managers, if required
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = media_serializers.PhotoSerializer

    def __init__(self, *args, **kwargs):
        self.photo_response_include_fields = ['id', 'title', 'pub_date', 'photo', 'note', 'tags', 'extension', 'photo_64']
        super(TrackerBomBomTypePhotoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            list_method = 'list_{}_boms'.format(self.kwargs['type'])
            bom = getattr(profile, list_method)().get(id=self.kwargs.get('pk'))
            qs_method = 'list_{}_bom_photos'.format(self.kwargs['type'])
            self.queryset = getattr(profile, qs_method)(bom=bom)
            return super(TrackerBomBomTypePhotoListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProjectAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerBomBomTypeVideoListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all sent boms photos
    # Todo: Use managers, if required
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = media_serializers.VideoSerializer

    def __init__(self, *args, **kwargs):
        self.video_response_include_fields = ['id', 'title', 'pub_date', 'video', 'note', 'tags', 'extension']
        super(TrackerBomBomTypeVideoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            list_method = 'list_{}_boms'.format(self.kwargs['type'])
            bom = getattr(profile, list_method)().get(id=self.kwargs.get('pk'))
            qs_method = 'list_{}_bom_videos'.format(self.kwargs['type'])
            self.queryset = getattr(profile, qs_method)(bom=bom)
            return super(TrackerBomBomTypeVideoListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProjectAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerBomRowMixin(
        JWTPayloadMixin):
    """
    Company BomRow Mixin
    """
    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            if 'bom_type' in self.kwargs:
                get_method = 'get_{}_bomrow'.format(self.kwargs['bom_type'])
                bomrow = getattr(profile, get_method)(self.kwargs.get('pk', None))
            else:
                bomrow = profile.get_bomrow(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, bomrow)
            return bomrow
        except ObjectDoesNotExist as err:
            raise django_api_exception.BomRowAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.BomRowSerializer
        else:
            self.serializer_class = output_serializer


class TrackerBomBomRowAddView(
        WhistleGenericViewMixin,
        TrackerBomRowMixin,
        generics.CreateAPIView):
    """
    Add a company bomrow w.r.t. bom
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.BomRowAddSerializer

    def __init__(self, *args, **kwargs):
        self.bomrow_request_include_fields = [
            'bom', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.bomrow_response_include_fields = [
            'id', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]

        super(TrackerBomBomRowAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True

        request.data['bom'] = self.kwargs.get('pk', None)
        return self.create(request, *args, **kwargs)


class TrackerBomBomRowListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get company all bomrows w.r.t. bom
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.BomRowSerializer

    def __init__(self, *args, **kwargs):
        self.bomrow_response_include_fields = [
            'id', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]
        super(TrackerBomBomRowListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_bomrows(self.kwargs.get('pk'))
        return super(TrackerBomBomRowListView, self).get_queryset()


class TrackerBomBomTypeBomRowListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get company all bomrows w.r.t. bom
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.BomRowSerializer

    def __init__(self, *args, **kwargs):
        self.bomrow_response_include_fields = [
            'id', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]
        super(TrackerBomBomTypeBomRowListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        if 'type' in self.kwargs:
            list_method = 'list_{}_bomrows'.format(self.kwargs['type'])
            self.queryset = getattr(profile, list_method)(self.kwargs.get('pk'))
        else:
            self.queryset = profile.list_bomrows(self.kwargs.get('pk'))
        return super(TrackerBomBomTypeBomRowListView, self).get_queryset()


class TrackerBomRowDetailView(
        TrackerBomRowMixin,
        generics.RetrieveAPIView):
    """
    Get a company bomrow
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.BomRowSerializer

    def __init__(self, *args, **kwargs):
        self.bomrow_response_include_fields = [
            'id', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]
        super(TrackerBomRowDetailView, self).__init__(*args, **kwargs)


class TrackerBomRowBomTypeDetailView(
        TrackerBomRowMixin,
        generics.RetrieveAPIView):
    """
    Get a company bomrow
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.BomRowSerializer

    def __init__(self, *args, **kwargs):
        self.bomrow_response_include_fields = [
            'id', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]
        super(TrackerBomRowBomTypeDetailView, self).__init__(*args, **kwargs)


class TrackerBomRowEditView(
        WhistleGenericViewMixin,
        TrackerBomRowMixin,
        generics.RetrieveUpdateAPIView):
    """
    Update a company bomrow
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.BomRowEditSerializer

    def __init__(self, *args, **kwargs):
        self.bomrow_request_include_fields = [
            'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.bomrow_response_include_fields = [
            'id', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.typology_response_include_fields = [
            'code', 'name'
        ]
        self.category_response_include_fields= [
            'code', 'name'
        ]
        self.sub_category_response_include_fields= [
            'code', 'name'
        ]
        self.unit_response_include_fields = [
            'code'
        ]

        super(TrackerBomRowEditView, self).__init__(*args, **kwargs)


class TrackerBomRowDeleteView(
        WhistleGenericViewMixin,
        TrackerBomRowMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a company bomrow
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.BomRowSerializer

    def __init__(self, *args, **kwargs):
        self.bomrow_response_include_fields = [
            'id', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]

        super(TrackerBomRowDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_bomrow(instance)


class TrackerBomArchiveMixin(
        JWTPayloadMixin):
    """
    Company BomRow Mixin
    """
    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.BomArchiveSerializer
        else:
            self.serializer_class = output_serializer


class TrackerBomArchiveAddView(
        WhistleGenericViewMixin,
        TrackerBomArchiveMixin,
        generics.CreateAPIView):

    """
    Add a bom to archive
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.BomArchiveAddSerializer

    def __init__(self, *args, **kwargs):
        self.bomarchive_request_include_fields = [
            'bom', 'company'
        ]
        self.bomarchive_response_include_fields = [
            'id', 'bom', 'company'
        ]

        super(TrackerBomArchiveAddView, self).__init__(*args, **kwargs)


class TrackerQuotationMixin(
        JWTPayloadMixin):
    """
    Company Quotation Mixin
    """
    def get_object(self):
        try:

            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            if 'type' in self.kwargs:
                get_method = 'get_{}_quotation'.format(self.kwargs['type'])
                quotation = getattr(profile, get_method)(self.kwargs.get('pk', None))
            else:
                quotation = profile.get_quotation(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, quotation['quotation'])
            return quotation['quotation']
        except ObjectDoesNotExist as err:
            raise django_api_exception.QuotationAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.QuotationSerializer
        else:
            self.serializer_class = output_serializer


class TrackerQuotationSenderListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company quotations w.r.t. company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.QuotationSerializer

    def __init__(self, *args, **kwargs):
        self.quotation_response_include_fields = [
            'id', 'title', 'description', 'date_quotation',
            'deadline', 'bom', 'tags', 'status', 'is_valid', 'is_accepted'
        ]
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom',
            'deadline', 'tags', 'status', 'project'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'status'
        ]
        super(TrackerQuotationSenderListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = profile.list_sent_quotations()
            self.queryset = self.queryset.exclude(archived_quotations__company=profile.company)
            return super(TrackerQuotationSenderListView, self).get_queryset().select_related(
                'bom',
                'bom__project',
            )
        except ObjectDoesNotExist as err:
            raise django_api_exception.QuotationAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerQuotationReceiverListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company quotations w.r.t. company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.QuotationSerializer

    def __init__(self, *args, **kwargs):
        self.quotation_response_include_fields = [
            'id', 'title', 'description', 'date_quotation',
            'deadline', 'bom', 'tags', 'status', 'owner', 'is_valid', 'is_accepted'
        ]
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom',
            'deadline', 'tags', 'status', 'project'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'status'
        ]
        super(TrackerQuotationReceiverListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = profile.list_received_quotations()
            self.queryset = self.queryset.exclude(archived_quotations__company=profile.company)
            return super(TrackerQuotationReceiverListView, self).get_queryset().select_related(
                'bom',
                'bom__project',
            )
        except ObjectDoesNotExist as err:
            raise django_api_exception.QuotationAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerQuotationDraftListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all company quotations w.r.t. company
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.QuotationSerializer

    def __init__(self, *args, **kwargs):
        self.quotation_response_include_fields = [
            'id', 'title', 'description', 'date_quotation',
            'deadline', 'bom', 'tags', 'status', 'owner', 'is_valid', 'is_accepted'
        ]
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom',
            'deadline', 'tags', 'status', 'project'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'status'
        ]
        super(TrackerQuotationDraftListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = profile.list_draft_quotations()
            return super(TrackerQuotationDraftListView, self).get_queryset().select_related(
                'bom',
                'bom__project',
            )
        except ObjectDoesNotExist as err:
            raise django_api_exception.QuotationAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerQuotationDetailView(
        TrackerQuotationMixin,
        generics.RetrieveAPIView):
    """
    Get a company quotation
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.QuotationSerializer

    def __init__(self, *args, **kwargs):
        self.quotation_response_include_fields = [
            'id', 'title', 'description', 'date_quotation',
            'deadline', 'bom', 'tags', 'is_draft'
        ]
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom',
            'deadline', 'tags'
        ]
        super(TrackerQuotationDetailView, self).__init__(*args, **kwargs)


class TrackerQuotationTypeDetailView(
        TrackerQuotationMixin,
        generics.RetrieveAPIView):
    """
    Get a company quotation
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.QuotationSerializer

    def __init__(self, *args, **kwargs):
        self.quotation_response_include_fields = [
            'id', 'title', 'description', 'date_quotation',
            'deadline', 'bom', 'tags', 'owner', 'is_draft',
            'bom_rows_id_list', 'is_valid', 'is_accepted'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom',
            'deadline', 'tags'
        ]

        super(TrackerQuotationTypeDetailView, self).__init__(*args, **kwargs)


class TrackerBomQuotationAddView(
        WhistleGenericViewMixin,
        TrackerQuotationMixin,
        generics.CreateAPIView):
    """
    Add a company quotation w.r.t. bom
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.QuotationAddSerializer

    def __init__(self, *args, **kwargs):
        self.quotation_request_include_fields = [
            'bom', 'title', 'description', 'date_quotation',
            'deadline', 'tags', 'quotation_rows', 'is_draft',
            'is_completed'
        ]
        self.quotationrow_request_include_fields = [
            'bom_row', 'name', 'description', 'quantity',
            'price'
        ]
        self.quotation_response_include_fields = [
            'title', 'description', 'date_quotation',
            'deadline', 'tags', 'quotation_rows', 'is_draft', 'is_completed'
        ]
        self.quotationrow_response_include_fields = [
            'id', 'bom_row', 'name', 'description', 'total',
            'quantity', 'price'
        ]
        self.bomrow_response_include_fields = [
            'id', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]

        super(TrackerBomQuotationAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True

        request.data['bom'] = self.kwargs.get('pk', None)
        return self.create(request, *args, **kwargs)


class TrackerQuotationEditView(
        WhistleGenericViewMixin,
        TrackerQuotationMixin,
        generics.RetrieveUpdateAPIView):
    """
    Update a company quotation
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.QuotationEditSerializer

    def __init__(self, *args, **kwargs):
        self.quotation_request_include_fields = [
            'title', 'description', 'date_quotation',
            'deadline', 'tags', 'is_draft', 'is_completed', 'is_accepted'
        ]
        self.quotation_response_include_fields = [
            'id', 'title', 'description', 'date_quotation',
            'deadline', 'tags', 'bom'
        ]
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom',
            'deadline', 'tags', 'status', 'project'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'status'
        ]
        super(TrackerQuotationEditView, self).__init__(*args, **kwargs)


class TrackerQuotationAcceptView(
        WhistleGenericViewMixin,
        TrackerQuotationMixin,
        generics.RetrieveUpdateAPIView):
    """
    Update a company quotation
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.QuotationAcceptSerializer

    def __init__(self, *args, **kwargs):
        self.quotation_request_include_fields = [
            'title', 'description', 'date_quotation',
            'deadline', 'tags', 'is_draft', 'is_completed', 'is_accepted'
        ]
        self.quotation_response_include_fields = [
            'id', 'title', 'description', 'date_quotation',
            'deadline', 'tags', 'bom', 'is_accepted'
        ]
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom',
            'deadline', 'tags', 'status', 'project'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'status'
        ]
        super(TrackerQuotationAcceptView, self).__init__(*args, **kwargs)


class TrackerQuotationDeleteView(
        WhistleGenericViewMixin,
        TrackerQuotationMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a company quotation
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.QuotationSerializer

    def __init__(self, *args, **kwargs):
        self.quotation_request_include_fields = [
            'title', 'description', 'date_quotation',
            'deadline', 'tags'
        ]
        self.quotation_response_include_fields = [
            'id', 'title', 'description', 'date_quotation',
            'deadline', 'tags'
        ]
        super(TrackerQuotationDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_quotation(instance)


class TrackerQuotationArchiveMixin(
        JWTPayloadMixin):
    """
    Company BomRow Mixin
    """
    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.QuotationArchiveSerializer
        else:
            self.serializer_class = output_serializer


class TrackerQuotationArchiveAddView(
        WhistleGenericViewMixin,
        TrackerQuotationArchiveMixin,
        generics.CreateAPIView):

    """
    Add a bom to archive
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.QuotationArchiveAddSerializer

    def __init__(self, *args, **kwargs):
        self.quotationarchive_request_include_fields = [
            'quotation', 'company'
        ]
        self.quotationarchive_response_include_fields = [
            'id', 'quotation', 'company'
        ]

        super(TrackerQuotationArchiveAddView, self).__init__(*args, **kwargs)


class TrackerQuotationRowMixin(
        JWTPayloadMixin):
    """
    Company QuotationRow Mixin
    """
    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            quotationrow = profile.get_quotationrow(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, quotationrow)
            return quotationrow
        except ObjectDoesNotExist as err:
            raise django_api_exception.QuotationAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.QuotationRowSerializer
        else:
            self.serializer_class = output_serializer


class TrackerQuotationQuotationRowListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get company quotation rows w.r.t. quotation
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.QuotationRowSerializer

    def __init__(self, *args, **kwargs):
        self.quotationrow_response_include_fields = [
            'id', 'bom_row', 'name', 'description', 'total',
            'quantity', 'price'
        ]
        self.bomrow_response_include_fields = [
            'id', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]
        super(TrackerQuotationQuotationRowListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_quotationrows(self.kwargs.get('pk'))
        return super(TrackerQuotationQuotationRowListView, self).get_queryset()


class TrackerQuotationQuotationTypeQuotationRowListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get company quotation rows w.r.t. quotation
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.QuotationRowSerializer

    def __init__(self, *args, **kwargs):
        self.quotationrow_response_include_fields = [
            'id', 'bom_row', 'name', 'description', 'total',
            'quantity', 'price'
        ]
        self.bomrow_response_include_fields = [
            'id', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]
        super(TrackerQuotationQuotationTypeQuotationRowListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        if 'type' in self.kwargs:
            list_method = 'list_{}_quotationrows'.format(self.kwargs['type'])
            self.queryset = getattr(profile, list_method)(self.kwargs.get('pk'))
        else:
            self.queryset = profile.list_quotationrows(self.kwargs.get('pk'))
        return super(TrackerQuotationQuotationTypeQuotationRowListView, self).get_queryset()


class TrackerQuotationRowDetailView(
        TrackerQuotationRowMixin,
        generics.RetrieveAPIView):
    """
    Get a company quotation row
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.QuotationRowSerializer

    def __init__(self, *args, **kwargs):
        self.quotationrow_response_include_fields = [
            'id', 'bom_row', 'name', 'description', 'total',
            'quantity', 'price', 'quotation'
        ]
        self.bomrow_response_include_fields = [
            'id', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]
        super(TrackerQuotationRowDetailView, self).__init__(*args, **kwargs)


class TrackerBomRowQuotationRowAddView(
        WhistleGenericViewMixin,
        TrackerQuotationRowMixin,
        generics.CreateAPIView):
    """
    Add a company quotation row w.r.t. bom row, quotation
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.QuotationRowAddSerializer

    def __init__(self, *args, **kwargs):
        self.quotationrow_request_include_fields = [
            'bom_row', 'quotation', 'name', 'description', 'quantity',
            'price'
        ]
        self.quotationrow_response_include_fields = [
            'id', 'bom_row', 'name', 'description', 'total',
            'quantity', 'price'
        ]
        self.bomrow_response_include_fields = [
            'id', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]
        super(TrackerBomRowQuotationRowAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True

        request.data['bom_row'] = self.kwargs.get('bomrow_pk', None)
        request.data['quotation'] = self.kwargs.get('quotation_pk', None)
        return self.create(request, *args, **kwargs)


class TrackerQuotationRowEditView(
        WhistleGenericViewMixin,
        TrackerQuotationRowMixin,
        generics.RetrieveUpdateAPIView):
    """
    Update a company quotationrow
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.QuotationRowEditSerializer

    def __init__(self, *args, **kwargs):
        self.quotationrow_request_include_fields = [
            'bom_row', 'quotation', 'name', 'description', 'quantity',
            'price'
        ]
        self.quotationrow_response_include_fields = [
            'id', 'bom_row', 'name', 'description', 'total',
            'quantity', 'price'
        ]
        self.bomrow_response_include_fields = [
            'id', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.typology_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.category_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.sub_category_response_include_fields = [
            'code', 'name', 'description'
        ]
        super(TrackerQuotationRowEditView, self).__init__(*args, **kwargs)

    
class TrackerQuotationRowDeleteView(
        TrackerQuotationRowMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a company quotationrow
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.QuotationRowSerializer

    def __init__(self, *args, **kwargs):
        self.quotationrow_response_include_fields = [
            'id', 'bom_row', 'name', 'description', 'total',
            'quantity', 'price'
        ]
        self.bomrow_response_include_fields = [
            'id', 'typology', 'category', 'subcategory', 'product', 'name',
            'description', 'unit', 'quantity'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]

        super(TrackerQuotationRowDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_quotationrow(instance)


class TrackerOfferMixin(
        JWTPayloadMixin):
    """
    Company Offer Mixin
    """
    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            offer = profile.get_offer(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, offer)
            return offer
        except ObjectDoesNotExist as err:
            raise django_api_exception.OfferAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.OfferSerializer
        else:
            self.serializer_class = output_serializer


class TrackerOfferDetailView(
        TrackerOfferMixin,
        generics.RetrieveAPIView):
    """
    Get a single company offer
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.OfferSerializer

    def __init__(self, *args, **kwargs):
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date', 'photo', 'owner', 'start_date',
            'deadline', 'price', 'tags', 'status', 'product', 'unit', 'followers',
            'buyers', 'is_draft'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description', 'subcategory'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        self.company_response_include_fields = [
            'id', 'name'
        ]
        super(TrackerOfferDetailView, self).__init__(*args, **kwargs)


class TrackerOfferListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get company offers
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.OfferSerializer

    def __init__(self, *args, **kwargs):
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date',
            'deadline',  'start_date', 'price', 'tags', 'status'
        ]
        super(TrackerOfferListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_offers()
        return super(TrackerOfferListView, self).get_queryset()


class TrackerReceivedOffersListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get company offers
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.OfferSerializer

    def __init__(self, *args, **kwargs):
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date', 'photo', 'start_date',
            'deadline', 'price', 'tags', 'status', 'product', 'followers', 'buyers', 'unit'
        ]
        self.product_response_include_fields = ['code', 'name']
        self.unit_response_include_fields = ['code']
        super(TrackerReceivedOffersListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_received_offers()
        filters = self.get_filters()
        excludes = self.get_excludes()
        order_by = self.get_order_by()
        queryset = super(QuerysetMixin, self).get_queryset()
        if filters:
            if isinstance(filters, dict):
                queryset = queryset.filter(**filters)
            else:
                queryset = queryset.filter(filters)
        if excludes:
            queryset = queryset.exclude(**excludes)
        if order_by:
            queryset = queryset.order_by(*order_by).distinct()
        return queryset

    def get_filters(self):
        filters = dict()
        for key, value in self.request.GET.items():
            if key.startswith('filter__'):
                key = key[8:]
                if key == 'product__code':
                    filters['product__code__in'] = value.split(',')[:-1]
                else:
                    if key.endswith('__isnull'):
                        filters[key] = json.loads(value.lower())
                    else:
                        filters[key] = value
        return filters


class TrackerReceivedFavouriteOffersListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get company offers
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.OfferSerializer

    def __init__(self, *args, **kwargs):
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date', 'photo', 'start_date',
            'deadline', 'price', 'tags', 'status', 'product', 'followers', 'buyers', 'unit'
        ]
        self.product_response_include_fields = ['code', 'name']
        self.unit_response_include_fields = ['code']
        super(TrackerReceivedFavouriteOffersListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_received_favourite_offers()
        return super(TrackerReceivedFavouriteOffersListView, self).get_queryset()


class TrackerReceivedRequiredOffersListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get company offers
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.OfferSerializer

    def __init__(self, *args, **kwargs):
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date', 'photo', 'start_date',
            'deadline', 'price', 'tags', 'status', 'product', 'followers', 'buyers', 'unit'
        ]
        self.product_response_include_fields = ['code', 'name']
        self.unit_response_include_fields = ['code']
        super(TrackerReceivedRequiredOffersListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_received_required_offers()
        return super(TrackerReceivedRequiredOffersListView, self).get_queryset()


class TrackerSentOffersListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get company offers
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.OfferSerializer

    def __init__(self, *args, **kwargs):
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date', 'photo', 'start_date',
            'deadline', 'price', 'tags', 'status', 'product', 'followers', 'buyers', 'unit'
        ]

        self.product_response_include_fields = ['code', 'name']
        self.unit_response_include_fields = ['code']
        super(TrackerSentOffersListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_sent_offers()
        return super(TrackerSentOffersListView, self).get_queryset()


class TrackerDraftOffersListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get company offers
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.OfferSerializer

    def __init__(self, *args, **kwargs):
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date', 'photo', 'start_date',
            'deadline', 'price', 'tags', 'status', 'product', 'followers', 'buyers', 'unit'
        ]
        self.product_response_include_fields = ['code', 'name']
        self.unit_response_include_fields = ['code']
        super(TrackerDraftOffersListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_draft_offers()
        return super(TrackerDraftOffersListView, self).get_queryset()


class TrackerOfferAddView(
        WhistleGenericViewMixin,
        TrackerOfferMixin,
        generics.CreateAPIView):
    """
    Add a single company offer
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.OfferAddSerializer

    def __init__(self, *args, **kwargs):
        self.offer_request_include_fields = [
            'title', 'description', 'deadline', 'start_date',
            'price', 'tags', 'photo', 'product', 'unit'
        ]
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date', 'start_date',
            'deadline', 'price', 'tags', 'status', 'is_draft', 'followers', 'photo', 'product', 'unit'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        super(TrackerOfferAddView, self).__init__(*args, **kwargs)


class TrackerOfferEditView(
        WhistleGenericViewMixin,
        TrackerOfferMixin,
        generics.RetrieveUpdateAPIView):
    """
    Update a single company offer
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.OfferEditSerializer

    def __init__(self, *args, **kwargs):
        self.offer_request_include_fields = [
            'title', 'description', 'deadline', 'start_date',
            'price', 'tags', 'is_draft', 'photo', 'product', 'unit'
        ]
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date', 'start_date', 'photo',
            'deadline', 'price', 'tags', 'status', 'is_draft', 'followers', 'product', 'unit'
        ]
        self.product_response_include_fields = [
            'code', 'name', 'description'
        ]
        self.unit_response_include_fields = [
            'code'
        ]
        super(TrackerOfferEditView, self).__init__(*args, **kwargs)

    def put(self, request, *args, **kwargs):
        if not 'photo' in request.data or type(request.data['photo']) == str:
            self.offer_request_include_fields.remove('photo')
        return super(TrackerOfferEditView, self).put(request, *args, **kwargs)


class TrackerOfferEnableView(
        WhistleGenericViewMixin,
        TrackerOfferMixin,
        generics.RetrieveUpdateAPIView):
    """
    Enable a company offer
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.OfferEnableSerializer

    def __init__(self, *args, **kwargs):
        self.offer_request_include_fields = []
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date', 'start_date',
            'deadline', 'price', 'tags', 'status'
        ]
        super(TrackerOfferEnableView, self).__init__(*args, **kwargs)


class TrackerOfferDisableView(
        WhistleGenericViewMixin,
        TrackerOfferMixin,
        generics.RetrieveUpdateAPIView):
    """
    Disable a company offer
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.OfferDisableSerializer

    def __init__(self, *args, **kwargs):
        self.offer_request_include_fields = []
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date', 'start_date',
            'deadline', 'price', 'tags', 'status'
        ]
        super(TrackerOfferDisableView, self).__init__(*args, **kwargs)


class TrackerOfferDeleteView(
        WhistleGenericViewMixin,
        TrackerOfferMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a single company offer
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.OfferSerializer

    def __init__(self, *args, **kwargs):
        self.offer_response_include_fields = [
            'id', 'title', 'description', 'pub_date', 'start_date',
            'deadline', 'price', 'tags', 'status'
        ]
        super(TrackerOfferDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_offer(instance)


class FollowOfferMixin(
        JWTPayloadMixin):
    """
    Offer Mixin
    """
    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.FavouriteOfferSerializer
        else:
            self.serializer_class = output_serializer


class TrackerOfferFollowView(
        WhistleGenericViewMixin,
        FollowOfferMixin,
        generics.CreateAPIView):
    """
    Follow a offer
    """
    serializer_class = serializers.SetFavouriteOfferSerializer

    def __init__(self, *args, **kwargs):
        self.favourite_request_include_fields = [
            'offer'
        ]
        self.favourite_response_include_fields = [
            'id', 'offer'
        ]
        self.offer_response_include_fields = [
            'id', 'title'
        ]
        super(TrackerOfferFollowView, self).__init__(*args, **kwargs)


class TrackerOfferUnFollowView(
        FollowOfferMixin,
        generics.RetrieveDestroyAPIView):
    """
    Unfollow a company
    """
    queryset = FavouriteOffer.objects.all()
    serializer_class = serializers.FavouriteOfferSerializer
    lookup_field = 'offer_id'

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.unfollow_offer(instance.offer)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        return FavouriteOffer.objects.filter(profile=profile)


class BuyOfferMixin(
        JWTPayloadMixin):
    """
    Offer Mixin
    """
    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.BoughtOfferSerializer
        else:
            self.serializer_class = output_serializer


class TrackerOfferBuyView(
        WhistleGenericViewMixin,
        BuyOfferMixin,
        generics.CreateAPIView):
    """
    Follow a offer
    """
    serializer_class = serializers.BuyOfferSerializer

    def __init__(self, *args, **kwargs):
        self.bought_request_include_fields = [
            'offer'
        ]
        self.bought_response_include_fields = [
            'id', 'offer'
        ]
        self.offer_response_include_fields = [
            'id', 'title'
        ]
        super(TrackerOfferBuyView, self).__init__(*args, **kwargs)


class TrackerOfferCancelBuyView(
        generics.RetrieveDestroyAPIView):
    """
    Unfollow a company
    """
    queryset = BoughtOffer.objects.all()
    serializer_class = serializers.BoughtOfferSerializer
    lookup_field = 'offer_id'

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.cancel_buy_offer(instance.offer)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        return BoughtOffer.objects.filter(profile=profile)


class TrackerCertificationMixin(
        JWTPayloadMixin):
    """
    Company Certification Mixin
    """
    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            cert = profile.get_certification(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, cert)
            return cert
        except ObjectDoesNotExist as err:
            raise django_api_exception.CertificationAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.CertificationSerializer
        else:
            self.serializer_class = output_serializer


class TrackerCertificationDetailView(
        TrackerCertificationMixin,
        generics.RetrieveAPIView):
    """
    Get a single company certification
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.CertificationSerializer

    def __init__(self, *args, **kwargs):
        self.certification_response_include_fields = [
            'id', 'title', 'description', 'document', 'status'
        ]
        super(TrackerCertificationDetailView, self).__init__(*args, **kwargs)


class TrackerCertificationListView(
        JWTPayloadMixin,
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get company certifications
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.CertificationSerializer

    def __init__(self, *args, **kwargs):
        self.certification_response_include_fields = [
            'id', 'title', 'description', 'document', 'status'
        ]
        super(TrackerCertificationListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_certifications()
        return super(TrackerCertificationListView, self).get_queryset()


class TrackerCertificationAddView(
        WhistleGenericViewMixin,
        TrackerCertificationMixin,
        generics.CreateAPIView):
    """
    Add a single company certification
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.CertificationAddSerializer

    def __init__(self, *args, **kwargs):
        self.certification_request_include_fields = [
            'title', 'description', 'document'
        ]
        self.certification_response_include_fields = [
            'id', 'title', 'description', 'document', 'status'
        ]
        super(TrackerCertificationAddView, self).__init__(*args, **kwargs)


class TrackerCertificationEditView(
        WhistleGenericViewMixin,
        TrackerCertificationMixin,
        generics.RetrieveUpdateAPIView):
    """
    Update a single company certification
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.CertificationEditSerializer

    def __init__(self, *args, **kwargs):
        self.certification_request_include_fields = [
            'title', 'description', 'document'
        ]
        self.certification_response_include_fields = [
            'id', 'title', 'description', 'document', 'status'
        ]
        super(TrackerCertificationEditView, self).__init__(*args, **kwargs)


class TrackerCertificationEnableView(
        WhistleGenericViewMixin,
        TrackerCertificationMixin,
        generics.RetrieveUpdateAPIView):
    """
    Enable a company certification
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.CertificationEnableSerializer

    def __init__(self, *args, **kwargs):
        self.certification_request_include_fields = []
        self.certification_response_include_fields = [
            'id', 'title', 'description', 'document', 'status'
        ]
        super(TrackerCertificationEnableView, self).__init__(*args, **kwargs)


class TrackerCertificationDisableView(
        WhistleGenericViewMixin,
        TrackerCertificationMixin,
        generics.RetrieveUpdateAPIView):
    """
    Disable a company certification
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.CertificationDisableSerializer

    def __init__(self, *args, **kwargs):
        self.certification_request_include_fields = []
        self.certification_response_include_fields = [
            'id', 'title', 'description', 'document', 'status'
        ]
        super(TrackerCertificationDisableView, self).__init__(*args, **kwargs)


class TrackerCertificationDeleteView(
        WhistleGenericViewMixin,
        TrackerCertificationMixin,
        generics.RetrieveDestroyAPIView):
    """
    Delete a single company certification
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.CertificationSerializer

    def __init__(self, *args, **kwargs):
        self.certification_response_include_fields = [
            'id', 'title', 'description', 'document', 'status'
        ]
        super(TrackerCertificationDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_certification(instance)
