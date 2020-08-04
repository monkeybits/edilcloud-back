# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext as _

from web.core.admin import UserAdminMixin
from . import models


class TeamInlineAdmin(admin.TabularInline):
    model = models.Team
    extra = 0
    exclude = (
        'creator', 'last_modifier', 'date_create',
        'date_last_modify', 'ordering',
    )
    raw_id_fields = ('profile',)


class TaskInlineAdmin(admin.TabularInline):
    model = models.Task
    extra = 0
    exclude = (
         'date_create', 'date_last_modify',
         'ordering',
    )
    raw_id_fields = (
        'assigned_company', 'shared_task',
        'creator', 'last_modifier'
    )


class TaskTeamInlineAdmin(admin.TabularInline):
    model = models.Activity
    extra = 0
    exclude = (
        'creator', 'last_modifier', 'date_create',
        'date_last_modify', 'ordering',
    )
    raw_id_fields = ('task', 'profile', )
    verbose_name_plural = _('Task Workers')

class ProjectAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/project/project.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'company', 'referent',
                'name', 'description',
                'date_start', 'date_end', 'tags', 'logo', 'note'
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
    inlines = (TeamInlineAdmin, TaskInlineAdmin,)
    list_display = (
        'id', 'status', 'company', 'logo',
        'referent',
        'name', 'get_members_count', 'get_tasks_count',
        'date_start', 'date_end', 'tags', 'get_completed_perc'
    )
    readonly_fields = (
        'creator', 'date_create', 'last_modifier',
        'date_last_modify',
    )
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE
    show_full_result_count = False
    list_editable = ('status',)
    list_filter = (
        'status',
    )
    search_fields = (
        'company__name', 'name', 'description',
        'tags',
    )
    raw_id_fields = ('company', 'referent',)

class TaskAdmin(UserAdminMixin, admin.ModelAdmin):
    class Media:
        js = (
            'js/project/task.js',
        )
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'project', 'name', 'shared_task', 'assigned_company',
                'date_start', 'date_end', 'date_completed', 'progress',
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
    inlines = (TaskTeamInlineAdmin,)
    list_display = (
        'id', 'status', 'project',
        'name', 'shared_task', 'assigned_company', 'date_start',
        'date_end', 'date_completed', 'progress',
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
        'project__name', 'name', 'assigned_company__name',
    )
    raw_id_fields = ('project', 'shared_task', 'assigned_company',)

class PostAdmin(UserAdminMixin, admin.ModelAdmin):
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'sub_task', 'author',
                'text', 'photos'
            )
        }),
    )
    list_display = (
        'id', 'author', 'sub_task',
        'text'
    )
    readonly_fields = (
        'created_date', 'published_date',
    )
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE

class CommentAdmin(UserAdminMixin, admin.ModelAdmin):
    fieldsets = (
        (_('general_information'), {
            'fields': (
                'parent', 'post',
                'author', 'text'
            )
        }),
    )
    list_display = (
        'id', 'author', 'post',
        'parent'
    )
    readonly_fields = (
        'created_date',
    )
    list_per_page = settings.DJANGO_ADMIN_LIST_PER_PAGE

admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Task, TaskAdmin)
admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Comment, CommentAdmin)
