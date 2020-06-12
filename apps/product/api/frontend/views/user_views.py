# -*- coding: utf-8 -*-

from rest_framework import generics

from web.api.views import QuerysetMixin
from .. import serializers
from .... import models


class UnitListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all units
    """
    queryset = models.Unit.objects.active()
    serializer_class = serializers.UnitSerializer

    def __init__(self, *args, **kwargs):
        self.unit_response_include_fields = ['code']
        super(UnitListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return super(UnitListView, self).get_queryset()


class TypologyListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all typologies
    """
    queryset = models.Typology.objects.active()
    serializer_class = serializers.TypologySerializer

    def __init__(self, *args, **kwargs):
        self.typology_response_include_fields = ['code', 'name', 'description', 'complete_name', 'color']
        super(TypologyListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return super(TypologyListView, self).get_queryset()


class TypologyDetailView(
        generics.RetrieveAPIView):
    """
    Get a single typology w.r.t. typology ID
    """
    queryset = models.Typology.objects.active()
    serializer_class = serializers.TypologySerializer
    lookup_field = 'code'

    def __init__(self, *args, **kwargs):
        self.typology_response_include_fields = ['code', 'name', 'description']
        super(TypologyDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return super(TypologyDetailView, self).get_queryset().filter(
            code=self.kwargs.get('code', None)
        )


class CategoryListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all categories w.r.t topology
    """
    queryset = models.Category.objects.active()
    serializer_class = serializers.CategorySerializer
    lookup_field = 'code'

    def __init__(self, *args, **kwargs):
        self.category_response_include_fields = ['code', 'name', 'description', 'complete_name', 'color']
        super(CategoryListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return super(CategoryListView, self).get_queryset().get_categories(
            typology_id=self.kwargs.get('code', None)
        )


class CategoryDetailView(
        generics.RetrieveAPIView):
    """
    Get a single category w.r.t. category ID
    """
    queryset = models.Category.objects.active()
    serializer_class = serializers.CategorySerializer
    lookup_field = 'code'

    def __init__(self, *args, **kwargs):
        self.category_response_include_fields = ['code', 'name', 'description', 'typology', 'color']
        super(CategoryDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return super(CategoryDetailView, self).get_queryset().filter(
            code=self.kwargs.get('code', None)
        )

class AllCategoryListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all categories
    """
    queryset = models.Category.objects.active()
    serializer_class = serializers.CategorySerializer
    lookup_field = 'code'

    def __init__(self, *args, **kwargs):
        self.category_response_include_fields = ['code', 'name', 'description', 'complete_name', 'color']
        super(AllCategoryListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return super(AllCategoryListView, self).get_queryset().order_by('typology')


class AllProductListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all categories
    """
    queryset = models.Product.objects.active()
    serializer_class = serializers.ProductSerializer
    lookup_field = 'code'

    def __init__(self, *args, **kwargs):
        self.product_response_include_fields = [
            'code', 'name'
        ]
        super(AllProductListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return super(AllProductListView, self).get_queryset()


class SubcategoryListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all subcategories w.r.t category
    """
    queryset = models.Subcategory.objects.active()
    serializer_class = serializers.SubcategorySerializer
    lookup_field = 'code'

    def __init__(self, *args, **kwargs):
        self.sub_category_response_include_fields = ['code', 'name', 'description', 'complete_name']
        super(SubcategoryListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return super(SubcategoryListView, self).get_queryset().get_sub_categories(
            category_id=self.kwargs.get('code', None)
        )


class SubcategoryDetailView(
        generics.RetrieveAPIView):
    """
    Get a single subcategory w.r.t. subcategory ID
    """
    queryset = models.Subcategory.objects.active()
    serializer_class = serializers.SubcategorySerializer
    lookup_field = 'code'

    def __init__(self, *args, **kwargs):
        self.sub_category_response_include_fields = ['code', 'name', 'description', 'category']
        super(SubcategoryDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return super(SubcategoryDetailView, self).get_queryset().filter(
            code=self.kwargs.get('code', None)
        )


class ProductListView(
        QuerysetMixin,
        generics.ListAPIView):
    """
    Get all products w.r.t subcategory
    """
    queryset = models.Product.objects.active()
    serializer_class = serializers.ProductSerializer
    lookup_field = 'code'

    def __init__(self, *args, **kwargs):
        self.product_response_include_fields = ['unit', 'code', 'name', 'description', 'complete_name']
        self.unit_response_include_fields = ['code']
        super(ProductListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return super(ProductListView, self).get_queryset().get_products(
            self.kwargs.get('code', None)
        )


class ProductDetailView(
        generics.RetrieveAPIView):
    """
    Get a single product w.r.t. product ID
    """
    queryset = models.Product.objects.active()
    serializer_class = serializers.ProductSerializer
    lookup_field = 'code'

    def __init__(self, *args, **kwargs):
        self.product_response_include_fields = ['unit', 'code', 'name', 'description']
        self.unit_response_include_fields = ['code']
        super(ProductDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return super(ProductDetailView, self).get_queryset().filter(
            code=self.kwargs.get('code', None)
        )
