# -*- coding: utf-8 -*-
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.quotation.api.frontend import serializers
from apps.quotation.models import Offer
from web.api.views import JWTPayloadMixin, WhistleGenericViewMixin


class UserOfferMixin(
        JWTPayloadMixin):
    """
    Profile Mixin
    """
    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.OfferSerializer
        else:
            self.serializer_class = output_serializer


class UserOfferDetailView(
        WhistleGenericViewMixin,
        UserOfferMixin,
        generics.RetrieveAPIView):
    """
    Get a single company offer
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.OfferSerializer
    queryset = Offer.objects.all()

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
        super(UserOfferDetailView, self).__init__(*args, **kwargs)
