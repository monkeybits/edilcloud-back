# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.profile.api.frontend.serializers import ProfileSerializer
from ... import models
from apps.product.api.frontend import serializers as product_serializers
from apps.profile.api.frontend import serializers as profile_serializers
from apps.project.api.frontend import serializers as project_serializers
from web.api.views import JWTPayloadMixin
from web.api.serializers import DynamicFieldsModelSerializer


class BomRowSerializer(
        DynamicFieldsModelSerializer):
    product = product_serializers.ProductSerializer()
    unit = product_serializers.UnitSerializer(read_only=True)
    typology = product_serializers.TypologySerializer(read_only=True)
    category = product_serializers.CategorySerializer(read_only=True)
    subcategory = product_serializers.SubcategorySerializer(read_only=True)
    product = product_serializers.ProductSerializer(read_only=True)

    class Meta:
        model = models.BomRow
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.bomrow_response_include_fields
        return super(BomRowSerializer, self).get_field_names(*args, **kwargs)


class BomRowAddSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):

    class Meta:
        model = models.BomRow
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.bomrow_request_include_fields
        return super(BomRowAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        bomrow = self.profile.create_bomrow(validated_data)
        return bomrow


class BomAndBomRowAddSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):
    bom_rows = BomRowAddSerializer(many=True)

    class Meta:
        model = models.Bom
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.bom_request_include_fields
        return super(BomAndBomRowAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        bom = self.profile.create_bom(validated_data)
        return bom


class BomSerializer(
        DynamicFieldsModelSerializer):
    owner = profile_serializers.CompanySerializer()
    contact = profile_serializers.ProfileSerializer()
    selected_companies = profile_serializers.CompanySerializer(many=True)
    bom_rows = BomRowSerializer(many=True)
    project = project_serializers.ProjectSerializer()

    class Meta:
        model = models.Bom
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.bom_response_include_fields
        return super(BomSerializer, self).get_field_names(*args, **kwargs)


class BomEditSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):

    class Meta:
        model = models.Bom
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.bom_request_include_fields
        return super(BomEditSerializer, self).get_field_names(*args, **kwargs)


class BomSendSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):

    class Meta:
        model = models.Bom
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def validate_selected_companies(self, selected_companies):
        if not selected_companies:
            raise serializers.ValidationError(
                _("at least one company category must be selected."))
        return selected_companies

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.bom_request_include_fields
        return super(BomSendSerializer, self).get_field_names(*args, **kwargs)


class BomArchiveSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = models.BomArchive
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.bomarchive_response_include_fields
        return super(BomArchiveSerializer, self).get_field_names(*args, **kwargs)


class BomArchiveAddSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):

    class Meta:
        model = models.BomArchive
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.bomarchive_request_include_fields
        return super(BomArchiveAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        archive = self.profile.archive_bom(validated_data)
        return archive


class BomRowEditSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):

    class Meta:
        model = models.BomRow
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.bomrow_request_include_fields
        return super(BomRowEditSerializer, self).get_field_names(*args, **kwargs)


class QuotationRowSerializer(
        DynamicFieldsModelSerializer):
    bom_row = BomRowSerializer()

    class Meta:
        model = models.QuotationRow
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.quotationrow_response_include_fields
        return super(QuotationRowSerializer, self).get_field_names(*args, **kwargs)


class QuotationSerializer(
        DynamicFieldsModelSerializer):
    bom = BomSerializer()
    owner = profile_serializers.CompanySerializer()
    contact = profile_serializers.ProfileSerializer()
    quotation_rows = QuotationRowSerializer(many=True)
    project = project_serializers.ProjectSerializer()
    bom_rows_id_list = serializers.SerializerMethodField()
    is_valid = serializers.BooleanField(source='is_valid_quotation')

    class Meta:
        model = models.Quotation
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.quotation_response_include_fields
        return super(QuotationSerializer, self).get_field_names(*args, **kwargs)

    def get_bom_rows_id_list(self, obj):
        return obj.get_bom_rows_id_list()


class QuotationRowAddSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):
    class Meta:
        model = models.QuotationRow
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.quotationrow_request_include_fields
        return super(QuotationRowAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        quotationrow = self.profile.create_quotationrow(validated_data)
        return quotationrow


class QuotationAddSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):
    quotation_rows = QuotationRowAddSerializer(many=True)

    class Meta:
        model = models.Quotation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.quotation_request_include_fields
        return super(QuotationAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        quotation = self.profile.create_quotation(validated_data)
        return quotation


class QuotationEditSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):
    class Meta:
        model = models.Quotation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.quotation_request_include_fields
        return super(QuotationEditSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        validated_data['id'] = instance.id
        quotation = self.profile.edit_quotation(validated_data)
        return quotation


class QuotationAcceptSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):
    class Meta:
        model = models.Quotation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.quotation_request_include_fields
        return super(QuotationEditSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        validated_data['id'] = instance.id
        quotation = self.profile.accept_quotation(validated_data)
        return quotation


class QuotationArchiveSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = models.QuotationArchive
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.quotationarchive_response_include_fields
        return super(QuotationArchiveSerializer, self).get_field_names(*args, **kwargs)


class QuotationArchiveAddSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):

    class Meta:
        model = models.QuotationArchive
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.quotationarchive_request_include_fields
        return super(QuotationArchiveAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        archive = self.profile.archive_quotation(validated_data)
        return archive


class QuotationRowEditSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):
    class Meta:
        model = models.QuotationRow
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.quotationrow_request_include_fields
        return super(QuotationRowEditSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        validated_data['id'] = instance.id
        quotationrow = self.profile.edit_quotationrow(validated_data)
        return quotationrow


class OfferSerializer(
        DynamicFieldsModelSerializer):
    contact = profile_serializers.ProfileSerializer()
    owner = profile_serializers.CompanySerializer()
    product = product_serializers.ProductSerializer()
    unit = product_serializers.UnitSerializer()
    followers = serializers.SerializerMethodField(read_only=True)
    buyers = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Offer
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.offer_response_include_fields
        return super(OfferSerializer, self).get_field_names(*args, **kwargs)

    def get_followers(self, obj):
        return [row.id for row in obj.followers.all()]

    def get_buyers(self, obj):
        return [row.id for row in obj.buyers.all()]


class OfferAddSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):
    class Meta:
        model = models.Offer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.offer_request_include_fields
        return super(OfferAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        offer = self.profile.create_offer(validated_data)
        return offer


class OfferEditSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):

    followers = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Offer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.offer_request_include_fields
        return super(OfferEditSerializer, self).get_field_names(*args, **kwargs)

    def get_followers(self, obj):
        return [row.id for row in obj.followers.all()]


class OfferEnableSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):
    class Meta:
        model = models.Offer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.offer_request_include_fields
        return super(OfferEnableSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        offer = self.profile.enable_offer(instance)
        return offer


class OfferDisableSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):
    class Meta:
        model = models.Offer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.offer_request_include_fields
        return super(OfferDisableSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        offer = self.profile.disable_offer(instance)
        return offer


class FavouriteOfferSerializer(
        DynamicFieldsModelSerializer):
    profile = ProfileSerializer()
    offer = OfferSerializer()

    class Meta:
        model = models.FavouriteOffer
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.favourite_response_include_fields
        return super(FavouriteOfferSerializer, self).get_field_names(*args, **kwargs)


class SetFavouriteOfferSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin):

    class Meta:
        model = models.FavouriteOffer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.favourite_request_include_fields
        return super(SetFavouriteOfferSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        favourite = self.profile.follow_offer(validated_data)
        return favourite


class BoughtOfferSerializer(
        DynamicFieldsModelSerializer):
    profile = ProfileSerializer()
    offer = OfferSerializer()

    class Meta:
        model = models.BoughtOffer
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.bought_response_include_fields
        return super(BoughtOfferSerializer, self).get_field_names(*args, **kwargs)


class BuyOfferSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin):

    class Meta:
        model = models.BoughtOffer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.bought_request_include_fields
        return super(BuyOfferSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        buy = self.profile.buy_offer(validated_data)
        return buy


class CertificationSerializer(
        DynamicFieldsModelSerializer):
    contact = profile_serializers.ProfileSerializer()
    owner = profile_serializers.CompanySerializer()

    class Meta:
        model = models.Certification
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.certification_response_include_fields
        return super(CertificationSerializer, self).get_field_names(*args, **kwargs)


class CertificationAddSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):
    class Meta:
        model = models.Certification
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.certification_request_include_fields
        return super(CertificationAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        certificate = self.profile.create_certification(validated_data)
        return certificate


class CertificationEditSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):
    class Meta:
        model = models.Certification
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.certification_request_include_fields
        return super(CertificationEditSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        validated_data['id'] = instance.id
        certificate = self.profile.edit_certification(validated_data)
        return certificate


class CertificationEnableSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):
    class Meta:
        model = models.Certification
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.certification_request_include_fields
        return super(CertificationEnableSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        certification = self.profile.enable_certification(instance)
        return certification


class CertificationDisableSerializer(
        DynamicFieldsModelSerializer,
        JWTPayloadMixin,
        serializers.ModelSerializer):
    class Meta:
        model = models.Certification
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.certification_request_include_fields
        return super(CertificationDisableSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        certification = self.profile.disable_certification(instance)
        return certification
