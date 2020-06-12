# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext as _

from web.core.admin import UserAdminMixin
from . import models


class BomRowInlineAdmin(admin.TabularInline):
    model = models.BomRow
    extra = 0
    exclude = (
        'creator', 'last_modifier', 'date_create',
        'date_last_modify',
    )
    readonly_fields = (
        'unit', 'typology', 'category',
        'subcategory', 'product',
    )


class BomSelectedCompaniesInlineAdmin(admin.TabularInline):
    model = models.Bom.selected_companies.through
    extra = 0


class BomAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/quotation/bom.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'title', 'description', 'project', 'owner',
                'contact', 'date_bom', 'deadline',
                'tags', 'is_draft'
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
    inlines = (BomSelectedCompaniesInlineAdmin, BomRowInlineAdmin)
    list_display = (
        'id', 'status', 'title', 'is_draft',
        'description', 'owner', 'contact',
        'get_bom_rows_count', 'date_bom', 'deadline',
        'get_selected_companies_count', 'get_selected_companies',
        'tags',
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
        'owner__name', 'title', 'description',
        'tags',
    )
    raw_id_fields = ('owner', 'contact', 'project',)


class QuotationRowInlineAdmin(admin.TabularInline):
    model = models.QuotationRow
    extra = 0
    exclude = (
        'creator', 'last_modifier', 'date_create',
        'date_last_modify', 'ordering',
    )
    readonly_fields = ('bom_row',)


class QuotationAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/quotation/quotation.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'title', 'description', 'owner',
                'contact', 'date_quotation', 'deadline',
                'bom', 'tags',
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
    inlines = (QuotationRowInlineAdmin,)
    list_display = (
        'id', 'title', 'description', 'status',
        'owner', 'contact', 'bom', 'get_quotation_rows_count',
        'date_quotation', 'deadline', 'tags',
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
        'owner__name', 'title', 'description',
        'tags',
    )
    raw_id_fields = ('owner', 'contact', 'bom',)


class OfferAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/quotation/offer.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'title', 'description', 'price',
                'owner', 'contact', 'deadline',
                'tags',
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
        'id', 'status', 'title',
        'description', 'price', 'owner',
        'contact', 'pub_date', 'deadline',
        'tags',
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
        'owner__name', 'title', 'description',
        'tags',
    )
    raw_id_fields = ('owner', 'contact',)


class CertificationAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/quotation/certification.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'title', 'description', 'owner',
                'document',
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
        'id', 'status', 'title',
        'description', 'document', 'owner',
        'date_create',
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
        'owner__name', 'title', 'description',
    )
    raw_id_fields = ('owner',)


admin.site.register(models.Bom, BomAdmin)
admin.site.register(models.Quotation, QuotationAdmin)
admin.site.register(models.Offer, OfferAdmin)
admin.site.register(models.Certification, CertificationAdmin)
