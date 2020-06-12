# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext as _

from web.core.admin import UserAdminMixin
from . import models


class UnitAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/product/unit.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': ('code',)
        }),
        (_('visualization_admin'), {
            'classes': ('collapse',),
            'fields': ('ordering', 'status')
        }),
        (_('logs_admin'), {
            'classes': ('collapse',),
            'fields': (
                'creator', 'date_create', 'last_modifier',
                'date_last_modify',
            )
        }),
    )
    list_display = (
        'code', 'status',
    )
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE
    show_full_result_count = False
    list_editable = ('status',)
    list_filter = ('status',)
    search_fields = ('code',)


class TypologyAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/product/typology.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'code', 'name', 'description', 'color'
            )
        }),
        (_('visualization_admin'), {
            'classes': ('collapse',),
            'fields': ('ordering', 'status')
        }),
        (_('logs_admin'), {
            'classes': ('collapse',),
            'fields': (
                'creator', 'date_create', 'last_modifier',
                'date_last_modify',
            )
        }),
    )
    list_display = (
        'code', 'status', 'name',
        'description',
    )
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE
    show_full_result_count = False
    list_editable = ('status',)
    list_filter = ('status',)
    search_fields = (
        'code', 'name', 'description',
    )


class CategoryAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/product/category.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'typology', 'code', 'name',
                'description',
            )
        }),
        (_('visualization_admin'), {
            'classes': ('collapse',),
            'fields': ('ordering', 'status')
        }),
        (_('logs_admin'), {
            'classes': ('collapse',),
            'fields': (
                'creator', 'date_create', 'last_modifier',
                'date_last_modify',
            )
        }),
    )
    list_display = (
        'code', 'status', 'typology',
        'name', 'description',
    )
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE
    show_full_result_count = False
    list_editable = ('status',)
    list_filter = ('status',)
    search_fields = (
        'typology__code', 'code', 'name',
        'description',
    )


class SubcategoryAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/product/subcategory.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'category', 'code', 'name',
                'description',
            )
        }),
        (_('visualization_admin'), {
            'classes': ('collapse',),
            'fields': ('ordering', 'status')
        }),
        (_('logs_admin'), {
            'classes': ('collapse',),
            'fields': (
                'creator', 'date_create', 'last_modifier',
                'date_last_modify',
            )
        }),
    )
    list_display = (
        'code', 'status', 'category',
        'name', 'description',
    )
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE
    show_full_result_count = False
    list_editable = ('status',)
    list_filter = ('status',)
    search_fields = (
        'category__code', 'code', 'name',
        'description',
    )


class ProductAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/product/product.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'subcategory', 'unit', 'code',
                'name', 'description', 'price',
            )
        }),
        (_('visualization_admin'), {
            'classes': ('collapse',),
            'fields': ('ordering', 'status')
        }),
        (_('logs_admin'), {
            'classes': ('collapse',),
            'fields': (
                'creator', 'date_create', 'last_modifier',
                'date_last_modify',
            )
        }),
    )
    list_display = (
        'code', 'status', 'subcategory',
        'unit', 'name', 'description',
        'price',
    )
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE
    show_full_result_count = False
    list_editable = ('status',)
    list_filter = ('status',)
    search_fields = (
        'subcategory__code', 'code', 'name',
        'description',
    )


admin.site.register(models.Unit, UnitAdmin)
admin.site.register(models.Typology, TypologyAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Subcategory, SubcategoryAdmin)
admin.site.register(models.Product, ProductAdmin)
