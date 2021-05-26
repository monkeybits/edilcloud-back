# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import user_views

user_urlpatterns = [
    url(
        r'^unit/$',
        user_views.UnitListView.as_view(),
        name='unit_list'
    ),
    url(
        r'^typology/$',
        user_views.TypologyListView.as_view(),
        name='typology_list'
    ),
    url(
        r'^typology/(?P<code>[-\w.%]+)/$',
        user_views.TypologyDetailView.as_view(),
        name='typology_detail'
    ),
    url(
        r'^typology/(?P<code>[-\w.%]+)/category_list/$',
        user_views.CategoryListView.as_view(),
        name='category_list'
    ),
    url(
        r'^category/$',
        user_views.AllCategoryListView.as_view(),
        name='all_category_list'
    ),
    url(
        r'^category/(?P<code>[-\w.%]+)/$',
        user_views.CategoryDetailView.as_view(),
        name='category_detail'
    ),
    url(
        r'^category/(?P<code>[-\w.%]+)/subcategory_list/$',
        user_views.SubcategoryListView.as_view(),
        name='subcategory_list'
    ),
    url(
        r'^subcategory/(?P<code>[-\w.%]+)/$',
        user_views.SubcategoryDetailView.as_view(),
        name='subcategory_detail'
    ),
    url(
        r'^subcategory/(?P<code>[-\w.%]+)/product_list/$',
        user_views.ProductListView.as_view(),
        name='product_list'
    ),
    url(
        r'^product/$',
        user_views.AllProductListView.as_view(),
        name='all_product_list'
    ),
    url(
        r'^product/(?P<code>[-\w.%]+)/$',
        user_views.ProductDetailView.as_view(),
        name='product_detail'
    ),
]

generic_urlpatterns = []

tracker_urlpatterns = []

urlpatterns = user_urlpatterns + generic_urlpatterns + tracker_urlpatterns
