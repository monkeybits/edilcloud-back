# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext as _
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from web.core.admin import UserAdminMixin
from . import models

User = get_user_model()

admin.site.unregister(User)


class CustomUserAdmin(UserAdmin):
    class Media:
        js = (
            'js/profile/user.js',
        )
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name',
        'is_staff', 'is_active', 'is_superuser',
        'profiles',
    )
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE
    show_full_result_count = False
    search_fields = (
        'username', 'email', 'first_name',
        'last_name',
    )

    def profiles(self, obj):
        return obj.profiles.count()

    profiles.short_description = _('profiles')


class FollowersInlineAdmin(admin.TabularInline):
    model = models.Favourite
    fk_name = 'company'
    fields = ('company_followed', 'invitation_date', 'approval_date')
    readonly_fields = (
        'company_followed', 'invitation_date', 'approval_date'
    )
    extra = 0
    verbose_name_plural = _('Company Following')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class MembersInlineAdmin(admin.TabularInline):
    # Todo: Add readonly_fields, if required
    model = models.Profile
    extra = 0
    verbose_name_plural = _('Company Members')
    readonly_fields = (
        'creator', 'last_modifier', 'date_create', 'date_last_modify',
        'user', 'status', 'get_invitation_status_icon',
        'role', 'first_name', 'last_name', 'email',
    )
    fields = (
        'status', 'user', 'role', 'first_name', 'last_name', 'email', 'get_invitation_status_icon',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_invitation_status_icon(self, obj):
        if obj.get_invitation_status() == settings.PROFILE_PROFILE_INVITATION_STATUS_PENDING:
            return format_html("<i class='fa fa-square-o' aria-hidden='true'></i>")
        if obj.get_invitation_status() == settings.PROFILE_PROFILE_INVITATION_STATUS_DENIED:
            return format_html("<i class='fa fa-square-o' aria-hidden='true'></i>")
        if obj.get_invitation_status() == settings.PROFILE_PROFILE_INVITATION_STATUS_APPROVED:
            return format_html("<i class='fa fa-check-square-o' aria-hidden='true'></i>")
    get_invitation_status_icon.short_description = _('invitation')


class PartnershipInviteInlineAdmin(admin.TabularInline):
    model = models.Partnership
    fk_name = 'inviting_company'
    fields = ('guest_company', 'invitation_date', 'approval_date')
    readonly_fields = ('guest_company', 'invitation_date', 'approval_date')
    verbose_name_plural = _('Inviting Partnership Companies')
    extra = 0


class PartnershipGuestInlineAdmin(admin.TabularInline):
    model = models.Partnership
    fk_name = 'guest_company'
    fields = ('inviting_company', 'invitation_date', 'approval_date')
    readonly_fields = ('inviting_company', 'invitation_date', 'approval_date')
    verbose_name_plural = _('Receipt Partnership Companies')
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CompanyAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/profile/company.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'name', 'slug', 'brand', 'description',
                'ssn', 'vat_number', 'url',
                'email', 'phone', 'phone2',
                'fax', 'logo', 'note',
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
    prepopulated_fields = {'slug': ('name',), }
    inlines = (
        FollowersInlineAdmin, MembersInlineAdmin, PartnershipInviteInlineAdmin,
        PartnershipGuestInlineAdmin
    )
    list_display = (
        'id', 'creator', 'status', 'name',
        'slug', 'ssn', 'vat_number',
        'url', 'email', 'get_profiles_count', 'get_owner_profiles_count',
        'get_delegate_profiles_count', 'get_level1_profiles_count',
        'get_level2_profiles_count', 'get_internal_projects_count',
        'get_shared_projects_count', 'get_boms_count', 'get_quotations_count',
        'get_offers_count', 'get_certifications_count',
    )
    list_editable = ('status',)
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE
    show_full_result_count = False
    list_filter = ('status',)
    search_fields = (
        'name', 'slug', 'ssn',
        'url', 'email',
    )


class PreferenceInlineAdmin(admin.TabularInline):
    model = models.Preference
    extra = 0
    exclude = (
        'creator', 'last_modifier', 'date_create',
        'date_last_modify', 'ordering',
    )


class ProfileAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/profile/profile.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'user', 'email', 'company', 'position',
                'last_name', 'first_name', 'language',
                'phone', 'fax', 'mobile',
                'info', 'role', 'note',
                'photo', 'company_invitation_date',
                'profile_invitation_date', 'invitation_refuse_date',
                'can_access_files', 'can_access_chat'
            )
        }),
        (_('visualization_admin'), {
            'classes': ('collapse',),
            'fields': ('ordering', 'status', 'is_superuser')
        }),
        (_('logs_admin'), {
            'classes': ('collapse',),
            'fields': (
                'creator', 'date_create', 'last_modifier',
                'date_last_modify',
            )
        }),
    )
    inlines = (PreferenceInlineAdmin,)
    list_display = (
        'id', 'status', 'user', 'position', 'is_superuser',
        'company', 'role', 'email', 'language',
        'last_name', 'first_name', 'company_invitation_date',
        'profile_invitation_date', 'invitation_refuse_date',
        'get_invitation_status_icon',
        'can_access_files', 'can_access_chat',
        'uidb36', 'token', 'get_accept_link', 'get_refuse_link'
    )
    list_editable = ('status',)
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE
    show_full_result_count = False
    list_filter = ('status',)
    search_fields = (
        'user__username', 'company__name', 'role',
        'email', 'language', 'last_name', 'first_name',
    )
    ordering = ('-id',)

    def get_invitation_status_icon(self, obj):
        if obj.get_invitation_status() == settings.PROFILE_PROFILE_INVITATION_STATUS_PENDING:
            return format_html("<i class='fa fa-square-o' aria-hidden='true'></i>")
        if obj.get_invitation_status() == settings.PROFILE_PROFILE_INVITATION_STATUS_DENIED:
            return format_html("<i class='fa fa-square' aria-hidden='true'></i>")
        if obj.get_invitation_status() == settings.PROFILE_PROFILE_INVITATION_STATUS_APPROVED:
            return format_html("<i class='fa fa-check-square-o' aria-hidden='true'></i>")
    get_invitation_status_icon.short_description = _('invitation')

    def get_accept_link(self, obj):
        if not obj.profile_invitation_date:
            return format_html("""
                <a href="{}" target="_blank">x</a>
            """.format(obj.get_accept_url()))
        return ""
    get_accept_link.short_description = _('invitation accept')

    def get_refuse_link(self, obj):
        if not obj.invitation_refuse_date:
            return format_html("""
                <a href="{}" target="_blank">x</a>
            """.format(obj.get_refuse_url()))
        return ""
    get_refuse_link.short_description = _('invitation refuse')


class FavouriteAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/profile/favourite.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': ('company', 'company_followed',)
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
        'id', 'company', 'company_followed', 'invitation_date', 'approval_date', 'refuse_date'
    )
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE
    show_full_result_count = False
    search_fields = (
        'company__name',
        'company_followed__name',
    )
    raw_id_fields = ('company_followed', 'company',)


class PartnershipAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/profile/partnership.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'inviting_company', 'guest_company',
                'approval_date', 'refuse_date'
            )
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
        'id', 'inviting_company', 'guest_company',
        'invitation_date', 'approval_date', 'refuse_date'
    )
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE
    show_full_result_count = False
    search_fields = (
        'inviting_company__name', 'guest_company__name',
    )
    raw_id_fields = ('inviting_company', 'guest_company',)


class SponsorAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/profile/sponsor.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'company', 'short_description', 'status', 'tags'
            )
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
        'id', 'company', 'short_description',
        'status',
    )
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE
    show_full_result_count = False
    search_fields = (
        'company', 'status',
    )



admin.site.register(User, CustomUserAdmin)

admin.site.register(models.Company, CompanyAdmin)

admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.MainProfile, ProfileAdmin)
admin.site.register(models.PhantomProfile, ProfileAdmin)
admin.site.register(models.GuestProfile, ProfileAdmin)
admin.site.register(models.OwnerProfile, ProfileAdmin)
admin.site.register(models.DelegateProfile, ProfileAdmin)
admin.site.register(models.Level1Profile, ProfileAdmin)
admin.site.register(models.Level2Profile, ProfileAdmin)

admin.site.register(models.Favourite, FavouriteAdmin)
admin.site.register(models.Partnership, PartnershipAdmin)
admin.site.register(models.Sponsor, SponsorAdmin)

