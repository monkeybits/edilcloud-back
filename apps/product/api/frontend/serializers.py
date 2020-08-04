# -*- coding: utf-8 -*-
from rest_framework import serializers

from ... import models
from web.api.serializers import DynamicFieldsModelSerializer


class UnitSerializer(
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Unit
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.unit_response_include_fields
        return super(UnitSerializer, self).get_field_names(*args, **kwargs)


class TypologySerializer(
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Typology
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.typology_response_include_fields
        return super(TypologySerializer, self).get_field_names(*args, **kwargs)


class CategorySerializer(
        DynamicFieldsModelSerializer):

    color = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Category
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.category_response_include_fields
        return super(CategorySerializer, self).get_field_names(*args, **kwargs)

    def get_color(self, obj):
        return obj.typology.color


class SubcategorySerializer(
        DynamicFieldsModelSerializer):
    class Meta:
        model = models.Subcategory
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.sub_category_response_include_fields
        return super(SubcategorySerializer, self).get_field_names(*args, **kwargs)


class ProductSerializer(
        DynamicFieldsModelSerializer):
    unit = UnitSerializer()

    class Meta:
        model = models.Product
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.product_response_include_fields
        return super(ProductSerializer, self).get_field_names(*args, **kwargs)
