# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime

from io import BytesIO
import operator
import zipfile
from functools import reduce
from io import BytesIO
from wsgiref.util import FileWrapper

import magic
import requests
from django.db.models import Q
from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from weasyprint import HTML, CSS
from apps.media.api.frontend.views.tracker_views import TrackerPhotoMixin, TrackerVideoMixin
from apps.project.models import Team, MediaAssignment, Comment, Post, Project, Activity
from web.api.permissions import RoleAccessPermission
from web.api.views import QuerysetMixin, JWTPayloadMixin, WhistleGenericViewMixin, DownloadViewMixin
from apps.project.api.frontend import serializers
from apps.media.api.frontend import serializers as media_serializers
from apps.document.api.frontend import serializers as document_serializers
from apps.message.api.frontend import serializers as message_serializers
from apps.quotation.api.frontend import serializers as quotation_serializers
from web import exceptions as django_exception
from web.drf import exceptions as django_api_exception
from web.settings import MEDIA_ROOT, PROJECT_PATH, BASE_DIR, STATIC_ROOT
from web.tasks import generate_pdf_report
from pdfreactor import api


class TrackerProjectMixin(
    JWTPayloadMixin):
    """
    Company Project Mixin
    """

    def get_profile(self):
        payload = self.get_payload()
        return self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_object(self):
        try:
            profile = self.get_profile()
            project = profile.get_project(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, project)
            return project
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.ProjectSerializer
        else:
            self.serializer_class = output_serializer


class TrackerProjectParentMixin(
    JWTPayloadMixin):
    """
    Company Project Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            project = profile.get_parent_project(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, project)
            return project
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.ProjectSerializer
        else:
            self.serializer_class = output_serializer


class TrackerMediaAttachmentMixin(JWTPayloadMixin):
    """
        Project media attachment Mixin
        """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            task = profile.get_task(self.kwargs.get('pk', None))
            document = task.mediaassignment_set.all().get(id=self.kwargs.get('pk2', None))
            self.check_object_permissions(self.request, document)
            return document
        except ObjectDoesNotExist as err:
            raise django_api_exception.DocumentAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.DocumentSerializer
        else:
            self.serializer_class = output_serializer


class TrackerProjectListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all internal and shared company projects w.r.t. profile
    # Todo: Use managers, if required
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProjectSerializer

    def __init__(self, *args, **kwargs):
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
            'company', 'referent', 'status', 'completed',
            'shared_companies', 'logo', 'address'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo'
        ]
        super(TrackerProjectListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_projects()
        return super(TrackerProjectListView, self).get_queryset()


class TrackerActivityPostListAlertView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.PostSerializer

    def __init__(self, *args, **kwargs):
        self.user_response_include_fields = [
            'id', 'username',
            'email', 'first_name', 'last_name', 'is_active'
        ]
        self.profile_response_include_fields = [
            'id', 'user', 'photo',
            'company', 'role', 'email', 'first_name', 'last_name'
        ]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        super(TrackerActivityPostListAlertView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_post_alert_all_activities()
        return super(TrackerActivityPostListAlertView, self).get_queryset()


class TrackerTaskPostListAlertView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.PostSerializer

    def __init__(self, *args, **kwargs):
        self.user_response_include_fields = [
            'id', 'username',
            'email', 'first_name', 'last_name', 'is_active'
        ]
        self.profile_response_include_fields = [
            'id', 'user', 'photo',
            'company', 'role', 'email', 'first_name', 'last_name'
        ]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        super(TrackerTaskPostListAlertView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_post_alert_all_tasks()
        return super(TrackerTaskPostListAlertView, self).get_queryset()


class TrackerProjectParentDetailView(
    TrackerProjectParentMixin,
    QuerysetMixin,
    generics.RetrieveAPIView):
    """
    Get a company project
    # Todo: Use managers, if required
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE)
    serializer_class = serializers.ProjectSerializer

    def __init__(self, *args, **kwargs):
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
            'company', 'referent', 'tags', 'profiles',
            'status', 'completed', 'messages_count', 'creator',
            'date_create', 'date_last_modify', 'typology',
            'shared_project', 'logo'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'position',
            'role', 'email', 'fax', 'phone'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(TrackerProjectParentDetailView, self).__init__(*args, **kwargs)


class TrackerProjectDetailView(
    TrackerProjectMixin,
    QuerysetMixin,
    generics.RetrieveAPIView):
    """
    Get a company project
    # Todo: Use managers, if required
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProjectSerializer

    def __init__(self, *args, **kwargs):
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
            'company', 'referent', 'tags', 'profiles',
            'status', 'completed', 'messages_count', 'creator',
            'date_create', 'date_last_modify', 'typology',
            'shared_project', 'date_create', 'note', 'logo', 'talks', 'address'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.talk_response_include_fields = ['id', 'code', 'content_type_name']
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'position',
            'role', 'email', 'fax', 'phone', 'company'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(TrackerProjectDetailView, self).__init__(*args, **kwargs)


class TrackerProjectAddView(
    WhistleGenericViewMixin,
    TrackerProjectMixin,
    generics.CreateAPIView):
    """
    Create a company project
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE)
    serializer_class = serializers.ProjectAddSerializer

    def __init__(self, *args, **kwargs):
        self.project_request_include_fields = [
            'name', 'description', 'date_start', 'date_end',
            'referent', 'tags', 'status', 'note', 'logo', 'address'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
            'company', 'referent', 'status', 'completed',
            'profiles', 'shared_companies', 'typology', 'logo', 'address'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerProjectAddView, self).__init__(*args, **kwargs)


class TrackerProjectEditView(
    WhistleGenericViewMixin,
    TrackerProjectMixin,
    generics.RetrieveUpdateAPIView):
    """
    Update a company project
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE)
    serializer_class = serializers.ProjectEditSerializer

    def __init__(self, *args, **kwargs):
        self.project_request_include_fields = [
            'name', 'description', 'date_start', 'date_end',
            'referent', 'tags', 'note', 'logo', 'address'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
            'company', 'referent', 'status', 'completed',
            'profiles', 'shared_companies', 'typology', 'logo', 'address'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerProjectEditView, self).__init__(*args, **kwargs)


class TrackerProjectEnableView(
    TrackerProjectMixin,
    generics.RetrieveUpdateAPIView):
    """
    Enable a company project
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE)
    serializer_class = serializers.ProjectEnableSerializer

    def __init__(self, *args, **kwargs):
        self.project_request_include_fields = []
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
            'company', 'referent', 'tags'
        ]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        self.profile_response_include_fields = ['id', 'first_name', 'position', 'last_name']
        super(TrackerProjectEnableView, self).__init__(*args, **kwargs)


class TrackerProjectDisableView(
    TrackerProjectMixin,
    generics.RetrieveUpdateAPIView):
    """
    Disable a company project
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE)
    serializer_class = serializers.ProjectDisableSerializer

    def __init__(self, *args, **kwargs):
        self.project_request_include_fields = []
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
            'company', 'referent', 'tags'
        ]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        self.profile_response_include_fields = ['id', 'first_name', 'position', 'last_name']
        super(TrackerProjectDisableView, self).__init__(*args, **kwargs)


class TrackerProjectDeleteView(
    TrackerProjectMixin,
    generics.RetrieveDestroyAPIView):
    """
    Delete a company project
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE)
    serializer_class = serializers.ProjectSerializer

    def __init__(self, *args, **kwargs):
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
            'company', 'referent',
        ]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        self.profile_response_include_fields = ['id', 'first_name', 'position', 'last_name']
        super(TrackerProjectDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        from apps.project.signals import close_project_notification
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        project = profile.get_project(instance.id)
        if project.creator == profile.user:
            close_project_notification(project._meta.model, project, **{'created': False})
            project.delete()


class TrackerProjectShareView(
    JWTPayloadMixin,
    generics.RetrieveAPIView):
    """
    Create a shared project
    #Todo: Need more information
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.ProjectSerializer

    def __init__(self, *args, **kwargs):
        self.project_request_include_fields = []
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
            'company', 'referent',
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'position', 'last_name'
        ]
        super(TrackerProjectShareView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = self.profile.list_projects()
        return super(TrackerProjectShareView, self).get_queryset()

    def get_object(self):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            filter_kwargs = {'pk': self.kwargs.get('pk', None)}
            obj = get_object_or_404(queryset, **filter_kwargs)
            self.profile.clone_project(obj)
            self.check_object_permissions(self.request, obj)
            return obj
        except django_exception.ProjectClonePermissionDenied as err:
            raise django_api_exception.ProjectCloneAPIPermissionDenied(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProjectBomSenderListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all company bill of materials
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = quotation_serializers.BomSerializer

    def __init__(self, *args, **kwargs):
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'owner', 'contact',
            'date_bom', 'deadline', 'selected_companies', 'tags'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerProjectBomSenderListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_project_sender_boms(self.kwargs.get('pk', None))
        return super(TrackerProjectBomSenderListView, self).get_queryset()


class TrackerProjectBomDraftListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all company bill of materials
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = quotation_serializers.BomSerializer

    def __init__(self, *args, **kwargs):
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'owner', 'contact',
            'date_bom', 'deadline', 'selected_companies',
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerProjectBomDraftListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_project_draft_boms(self.kwargs.get('pk', None))
        return super(TrackerProjectBomDraftListView, self).get_queryset()


class TrackerProjectBomReceiverListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all company bill of materials
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = quotation_serializers.BomSerializer

    def __init__(self, *args, **kwargs):
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'owner', 'contact',
            'date_bom', 'deadline', 'selected_companies',
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerProjectBomReceiverListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_project_receiver_boms(self.kwargs.get('pk', None))
        return super(TrackerProjectBomReceiverListView, self).get_queryset()


class TrackerProjectQuotationSenderListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all company quotations
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1,)
    serializer_class = quotation_serializers.QuotationSerializer

    def __init__(self, *args, **kwargs):
        self.quotation_response_include_fields = [
            'id', 'title', 'description', 'owner', 'contact', 'date_quotation',
            'deadline', 'bom', 'tags'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom', 'deadline'
        ]
        super(TrackerProjectQuotationSenderListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_project_sender_quotations(self.kwargs.get('pk', None))
        return super(TrackerProjectQuotationSenderListView, self).get_queryset()


class TrackerProjectQuotationDraftListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all company quotations
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = quotation_serializers.QuotationSerializer

    def __init__(self, *args, **kwargs):
        self.quotation_response_include_fields = [
            'id', 'title', 'description', 'owner', 'contact', 'date_quotation',
            'deadline', 'bom', 'tags'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom', 'deadline'
        ]
        super(TrackerProjectQuotationDraftListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_project_draft_quotations(self.kwargs.get('pk', None))
        return super(TrackerProjectQuotationDraftListView, self).get_queryset()


class TrackerProjectQuotationReceiverListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all company quotations
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1,)
    serializer_class = quotation_serializers.QuotationSerializer

    def __init__(self, *args, **kwargs):
        self.quotation_response_include_fields = [
            'id', 'title', 'description', 'owner', 'contact', 'date_quotation',
            'deadline', 'bom', 'tags', 'is_valid', 'is_accepted'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        self.bom_response_include_fields = [
            'id', 'title', 'description', 'date_bom', 'deadline'
        ]
        super(TrackerProjectQuotationReceiverListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_project_receiver_quotations(self.kwargs.get('pk', None))
        return super(TrackerProjectQuotationReceiverListView, self).get_queryset()


class TrackerProjectInternalActivityListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
        Get all activities of a company project task
        """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.TaskActivitySerializer

    def __init__(self, *args, **kwargs):
        self.activity_response_include_fields = [
            'id', 'task', 'profile', 'title', 'description', 'status',
            'datetime_start', 'datetime_end', 'alert'
        ]
        self.task_response_include_fields = [
            'id', 'project', 'name', 'date_start',
            'date_end', 'date_completed'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerProjectInternalActivityListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_task_internal_activities(self.kwargs.get('pk', None))
        return super(TrackerProjectInternalActivityListView, self).get_queryset()


class TrackerProjectParentActivityListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
        Get all activities of a company project task
        """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE)
    serializer_class = serializers.TaskActivitySerializer

    def __init__(self, *args, **kwargs):
        self.activity_response_include_fields = [
            'id', 'task', 'profile', 'title', 'description', 'status',
            'datetime_start', 'datetime_end', 'alert'
        ]
        self.task_response_include_fields = [
            'id', 'project', 'name', 'date_start',
            'date_end', 'date_completed'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerProjectParentActivityListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_project_parent_activities(self.kwargs.get('pk', None))
        return super(TrackerProjectParentActivityListView, self).get_queryset()


class TrackerProjectActivityListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
        Get all activities of a company project task
        """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.TaskActivitySerializer

    def __init__(self, *args, **kwargs):
        self.activity_response_include_fields = [
            'id', 'task', 'profile', 'title', 'description', 'status',
            'datetime_start', 'datetime_end', 'alert'
        ]
        self.task_response_include_fields = [
            'id', 'project', 'name', 'date_start',
            'date_end', 'date_completed'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerProjectActivityListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_project_task_activities(self.kwargs.get('pk', None))
        return super(TrackerProjectActivityListView, self).get_queryset()


class TrackerProjectParentTeamListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all team members w.r.t. project
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE)
    serializer_class = serializers.TeamSerializer

    def __init__(self, *args, **kwargs):
        self.team_response_include_fields = [
            'id', 'profile', 'role', 'status'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'position',
            'email', 'phone', 'note', 'role', 'language'
        ]
        super(TrackerProjectParentTeamListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = profile.list_parent_members(self.kwargs.get('pk'))
            return super(TrackerProjectParentTeamListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProjectAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProjectTeamListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all team members w.r.t. project
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.TeamSerializer

    def __init__(self, *args, **kwargs):
        self.team_response_include_fields = [
            'id', 'profile', 'role', 'status', 'project_invitation_date', 'disabled'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'position',
            'email', 'phone', 'note', 'role', 'language', 'company'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'color_project', 'logo', 'slug', 'email', 'tax_code'
        ]
        super(TrackerProjectTeamListView, self).__init__(*args, **kwargs)

    def get_filters(self):
        filters = super(TrackerProjectTeamListView, self).get_filters()
        if filters:
            if len(filters) != 1:
                query = []
                for key, value in enumerate(filters):
                    query.append(tuple((value, filters[value])))
                return reduce(operator.and_, [Q(x) for x in query])
        return filters

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            generic = 'list_' + self.kwargs.get('type') + '_members'
            self.queryset = getattr(profile, generic)(self.kwargs.get('pk'))
            # self.queryset = profile.list_members(self.kwargs.get('pk'))
            return super(TrackerProjectTeamListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProjectAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProjectTalkListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all project talks
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = message_serializers.TalkSerializer

    def __init__(self, *args, **kwargs):
        self.talk_response_include_fields = ['id', 'code']
        super(TrackerProjectTalkListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            project = profile.list_projects().get(id=self.kwargs.get('pk'))
            self.queryset = profile.list_project_talks(project=project)
            return super(TrackerProjectTalkListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProjectAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProjectParentMessageListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all project messages
    """
    serializer_class = message_serializers.MessageSerializer

    def __init__(self, *args, **kwargs):
        self.message_response_include_fields = [
            'id', 'body', 'sender', 'date_create', 'unique_code'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'position', 'role', 'company'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'category'
        ]
        super(TrackerProjectParentMessageListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        project = profile.get_parent_project(self.kwargs.get('pk'))
        self.queryset = profile.list_project_messages(project=project)
        return super(TrackerProjectParentMessageListView, self).get_queryset()


class TrackerProjectMessageListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all project messages
    """
    serializer_class = message_serializers.MessageSerializer

    def __init__(self, *args, **kwargs):
        self.message_response_include_fields = [
            'id', 'body', 'sender', 'date_create', 'unique_code'
        ]
        self.talk_response_include_fields = ['id', 'code', 'content_type_name', 'unread_count']
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'position', 'role', 'company'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'category', 'color_project'
        ]
        super(TrackerProjectMessageListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        project = profile.list_projects().get(id=self.kwargs.get('pk'))
        self.queryset = profile.list_project_messages(project=project)
        return super(TrackerProjectMessageListView, self).get_queryset()


class TrackerProjectPhotoListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get company all project photos
    # Todo: Use managers, if required
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = media_serializers.PhotoSerializer

    def __init__(self, *args, **kwargs):
        self.photo_response_include_fields = [
            'id', 'title', 'pub_date', 'photo',
            'extension', 'size', 'relative_path', 'folder_relative_path'
        ]
        super(TrackerProjectPhotoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            project = profile.list_projects().get(id=self.kwargs.get('pk'))
            self.queryset = profile.list_project_photos(project=project).distinct()
            return super(TrackerProjectPhotoListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProjectAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProjectVideoListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get company all project videos
    # Todo: Use managers, if required
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = media_serializers.VideoSerializer

    def __init__(self, *args, **kwargs):
        self.video_response_include_fields = [
            'id', 'title', 'pub_date', 'video',
            'extension', 'size', 'relative_path', 'folder_relative_path'
        ]
        super(TrackerProjectVideoListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            project = profile.list_projects().get(id=self.kwargs.get('pk'))
            self.queryset = profile.list_project_videos(project=project)
            return super(TrackerProjectVideoListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProjectAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProjectFolderListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get company all project folders
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = media_serializers.FolderSerializer

    def __init__(self, *args, **kwargs):
        self.photo_response_include_fields = [
            'id', 'name', 'is_public', 'is_root'
        ]
        super(TrackerProjectFolderListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            project = profile.list_projects().get(id=self.kwargs.get('pk'))
            self.queryset = profile.list_project_folders(project=project)
            return super(TrackerProjectFolderListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProjectAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProjectParentDocumentListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all project documents
    # Todo: Use managers, if required
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE)
    serializer_class = document_serializers.DocumentSerializer

    def __init__(self, *args, **kwargs):
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document', 'date_create'
        ]
        super(TrackerProjectParentDocumentListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = profile.list_project_parent_documents(self.kwargs.get('pk'))
            return super(TrackerProjectParentDocumentListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProjectAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProjectDocumentListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all project documents
    # Todo: Use managers, if required
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = document_serializers.DocumentSerializer

    def __init__(self, *args, **kwargs):
        self.document_response_include_fields = [
            'id', 'title', 'description', 'document', 'date_create',
            'extension', 'size', 'relative_path', 'folder_relative_path'
        ]
        super(TrackerProjectDocumentListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            project = profile.list_projects().get(id=self.kwargs.get('pk'))
            self.queryset = profile.list_project_documents(project=project)
            return super(TrackerProjectDocumentListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProjectAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProjectShowCaseListView(
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all project showcase
    """
    # Todo: Need more information
    pass


class TrackerProjectParentGanttIntervalDetailView(
    TrackerProjectParentMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get a company project gantt
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE)
    serializer_class = serializers.TaskSerializer

    def __init__(self, *args, **kwargs):
        self.task_response_include_fields = [
            'id', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'logo'
        ]
        super(TrackerProjectParentGanttIntervalDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = profile.list_parent_tasks_interval(
                self.kwargs.get('pk'), self.kwargs.get('month'), self.kwargs.get('year')
            )
            return super(TrackerProjectParentGanttIntervalDetailView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            ).order_by('date_start', 'date_end', 'id')


class TrackerProjectGanttIntervalDetailView(
    TrackerProjectMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get a company project gantt
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.TaskSerializer

    def __init__(self, *args, **kwargs):
        self.task_response_include_fields = [
            'id', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'shared_task'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'logo'
        ]
        super(TrackerProjectGanttIntervalDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = profile.list_internal_tasks_interval(
                self.get_object(), self.kwargs.get('month'), self.kwargs.get('year')
            ).order_by('date_start', 'date_end', 'id')
            return super(TrackerProjectGanttIntervalDetailView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProjectInternalGanttDetailView(
    TrackerProjectMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get a company project gantt
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.TaskSerializer

    def __init__(self, *args, **kwargs):
        self.task_response_include_fields = [
            'id', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'logo'
        ]
        super(TrackerProjectInternalGanttDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = profile.list_internal_tasks(self.get_object())
            return super(TrackerProjectInternalGanttDetailView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProjectGanttDetailView(
    TrackerProjectMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get a company project gantt
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.TaskSerializer

    def __init__(self, *args, **kwargs):
        self.task_response_include_fields = [
            'id', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'logo'
        ]
        super(TrackerProjectGanttDetailView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = profile.list_tasks(self.get_object())
            return super(TrackerProjectGanttDetailView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerTaskMixin(
    JWTPayloadMixin):
    """
    Company Project Task Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            task = profile.get_task(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, task)
            return task
        except ObjectDoesNotExist as err:
            raise django_api_exception.TaskAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.TaskSerializer
        else:
            self.serializer_class = output_serializer


class TrackerPostMixin(
    JWTPayloadMixin):
    """
    Company Project Task Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            task = profile.get_task(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, task)
            return task
        except ObjectDoesNotExist as err:
            raise django_api_exception.TaskAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.PostSerializer
        else:
            self.serializer_class = output_serializer


class TrackerPostEditMixin(
    JWTPayloadMixin):
    """
    Company Project Task Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            post = profile.get_post(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, post)
            return post
        except ObjectDoesNotExist as err:
            raise django_api_exception.TaskAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.PostSerializer
        else:
            self.serializer_class = output_serializer


class TrackerCommentEditMixin(
    JWTPayloadMixin):
    """
    Company Project Task Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            comment = profile.get_comment(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, comment)
            return comment
        except ObjectDoesNotExist as err:
            raise django_api_exception.TaskAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.CommentSerializer
        else:
            self.serializer_class = output_serializer


class TrackerPostObjectMixin(
    JWTPayloadMixin):
    """
    Company Project Task Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            post = profile.get_post(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, post)
            return post
        except ObjectDoesNotExist as err:
            raise django_api_exception.PostAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.PostSerializer
        else:
            self.serializer_class = output_serializer


class TrackerAttachmentMixin(JWTPayloadMixin):
    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            attachment = profile.get_attachment(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, attachment)
            return attachment
        except ObjectDoesNotExist as err:
            raise django_api_exception.PostAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.TaskAttachmentAddSerializer
        else:
            self.serializer_class = output_serializer


class TrackerCommentObjectMixin(
    JWTPayloadMixin):
    """
    Company Project Task Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            comment = profile.get_comment(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, comment)
            return comment
        except ObjectDoesNotExist as err:
            raise django_api_exception.CommentAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.CommentSerializer
        else:
            self.serializer_class = output_serializer


class TrackerProjectInternalTaskListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all tasks w.r.t. project
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE)
    serializer_class = serializers.TaskSerializer

    def __init__(self, *args, **kwargs):
        self.task_response_include_fields = [
            'id', 'project', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'status',
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'typology'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerProjectInternalTaskListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            project = profile.list_projects().get(pk=self.kwargs.get('pk'))
            self.queryset = profile.list_internal_tasks(project)
            return super(TrackerProjectInternalTaskListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProjectParentTaskListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all tasks w.r.t. project
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE)
    serializer_class = serializers.TaskSerializer

    def __init__(self, *args, **kwargs):
        self.task_response_include_fields = [
            'id', 'project', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'status',
            'share_status', 'shared_task'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'shared_project'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerProjectParentTaskListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = profile.list_parent_tasks(self.kwargs.get('pk'))
            return super(TrackerProjectParentTaskListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProjectTaskListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all tasks w.r.t. project
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.TaskSerializer

    def __init__(self, *args, **kwargs):
        self.task_response_include_fields = [
            'id', 'project', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'status',
            'share_status', 'shared_task', 'only_read',
            'alert', 'starred', 'note', 'activities', 'media_set'
        ]
        self.activity_response_include_fields = [
            'id', 'task', 'workers', 'title', 'description', 'status',
            'datetime_start', 'datetime_end', 'media_set', 'can_assign_in_activity', 'workers_in_activity',
            'alert'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'shared_project'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo', 'color_project'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerProjectTaskListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            project = profile.list_projects().get(pk=self.kwargs.get('pk'))
            self.queryset = profile.list_tasks(project)
            return super(TrackerProjectTaskListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerProjectsTasksActivitiesListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all tasks w.r.t. project
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.TaskSerializer

    def __init__(self, *args, **kwargs):
        self.task_response_include_fields = [
            'id', 'project', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'status',
            'share_status', 'shared_task', 'only_read',
            'alert', 'starred', 'note', 'activities', 'media_set'
        ]
        self.activity_response_include_fields = [
            'id', 'task', 'workers', 'title', 'description', 'status',
            'datetime_start', 'datetime_end', 'media_set', 'can_assign_in_activity', 'workers_in_activity', 'alert'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'shared_project'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerProjectsTasksActivitiesListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            projects = profile.list_projects()
            self.queryset = profile.list_projects_tasks(projects)
            return super(TrackerProjectsTasksActivitiesListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerGanttProjectTaskListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    """
    Get all tasks w.r.t. project
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.TaskSerializer

    def __init__(self, *args, **kwargs):
        self.task_response_include_fields = [
            'id', 'project', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'status',
            'share_status', 'shared_task', 'only_read',
            'alert', 'starred', 'note', 'activities', 'media_set'
        ]
        self.activity_response_include_fields = [
            'id', 'task', 'workers', 'title', 'description', 'status',
            'datetime_start', 'datetime_end', 'media_set', 'alert'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end', 'shared_project'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo', 'color_project'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerGanttProjectTaskListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            project = profile.list_projects().get(pk=self.kwargs.get('pk'))
            self.queryset = profile.list_tasks(project)
            return super(TrackerGanttProjectTaskListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProfileAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def list(self, request, *args, **kwargs):
        response = super(TrackerGanttProjectTaskListView, self).list(request, *args, **kwargs)
        data = response.data
        mix_list = []
        for d in data:
            activities = d.pop('activities')
            for a in activities:
                a['parent'] = 1
                mix_list.append(a)
            d['parent'] = 0
            mix_list.append(d)
        response.data = mix_list
        return response


class TrackerProjectTaskAddView(
    WhistleGenericViewMixin,
    TrackerTaskMixin,
    generics.CreateAPIView):
    """
    Create a project task
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TaskAddSerializer

    def __init__(self, *args, **kwargs):
        self.task_request_include_fields = [
            'project', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'shared_task', 'alert',
            'starred', 'note', 'progress'
        ]
        self.task_response_include_fields = [
            'id', 'project', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'status',
            'share_status', 'shared_task', 'alert',
            'starred', 'note', 'progress', 'media_set'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end',
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo', 'color_project'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo',
        ]
        super(TrackerProjectTaskAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True

        if request.data:
            if type(request.data) is list:
                for dat in request.data:
                    dat['project'] = self.kwargs.get('pk', None)

                serializer = self.get_serializer(data=request.data, many=True)
                serializer.is_valid(raise_exception=True)
                input_serializer = serializer.save()
                self.set_output_serializer()
                output_serializer = self.get_serializer(
                    self.serializer_class.Meta.model.objects.filter(project=self.kwargs.get('pk', None)), many=True)
                return Response(output_serializer.data, status=status.HTTP_201_CREATED)
            else:
                request.data['project'] = self.kwargs.get('pk', None)
                return self.create(request, *args, **kwargs)
        return self.create(request, *args, **kwargs)

    # def get_serializer(self, *args, **kwargs):
    #     return self.get_serializer_class()(data=self.request.data, many=True)


class TrackerTaskDetailView(
    TrackerTaskMixin,
    generics.RetrieveAPIView):
    """
    Get a project task
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TaskSerializer

    def __init__(self, *args, **kwargs):
        self.task_response_include_fields = [
            'id', 'project', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'status',
            'share_status', 'shared_task'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end',
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        super(TrackerTaskDetailView, self).__init__(*args, **kwargs)


class TrackerTaskShareView(
    WhistleGenericViewMixin,
    TrackerTaskMixin,
    generics.RetrieveAPIView):
    """
    Update a project task
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TaskSerializer

    def __init__(self, *args, **kwargs):
        self.task_request_include_fields = []
        self.task_response_include_fields = [
            'id', 'project', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'status',
            'shared_task'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end',
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo',
        ]
        super(TrackerTaskShareView, self).__init__(*args, **kwargs)

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            task = profile.get_task(self.kwargs.get('pk', None))
            profile.share_task(task)
            self.check_object_permissions(self.request, task)
            return task
        except ObjectDoesNotExist as err:
            raise django_api_exception.TaskAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerTaskCloneView(
    WhistleGenericViewMixin,
    TrackerTaskMixin,
    generics.RetrieveAPIView):
    """
    Update a project task
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TaskSerializer

    def __init__(self, *args, **kwargs):
        self.task_request_include_fields = []
        self.task_response_include_fields = [
            'id', 'project', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'status',
            'shared_task'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end',
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo',
        ]
        super(TrackerTaskCloneView, self).__init__(*args, **kwargs)

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            task = profile.get_generic_task(self.kwargs.get('pk', None))
            # task = profile.get_task(self.kwargs.get('pk', None))
            profile.clone_task(task)
            self.check_object_permissions(self.request, task)
            return task
        except ObjectDoesNotExist as err:
            raise django_api_exception.TaskAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerTaskEditView(
    WhistleGenericViewMixin,
    TrackerTaskMixin,
    generics.RetrieveUpdateAPIView):
    """
    Update a project task
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TaskEditSerializer

    def __init__(self, *args, **kwargs):
        self.task_request_include_fields = [
            'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'project', 'progress',
            'alert',
            'starred', 'note'
        ]
        self.task_response_include_fields = [
            'id', 'project', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'status', 'share_status',
            'alert',
            'starred', 'note'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end',
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        super(TrackerTaskEditView, self).__init__(*args, **kwargs)


class TrackerTaskEnableView(
    TrackerTaskMixin,
    generics.RetrieveUpdateAPIView):
    """
    Enable a project task
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TaskEnableSerializer

    def __init__(self, *args, **kwargs):
        self.task_request_include_fields = []
        self.task_response_include_fields = [
            'id', 'project', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'status',
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end',
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        super(TrackerTaskEnableView, self).__init__(*args, **kwargs)


class TrackerTaskDisableView(
    TrackerTaskMixin,
    generics.RetrieveUpdateAPIView):
    """
    Disable a project task
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TaskDisableSerializer

    def __init__(self, *args, **kwargs):
        self.task_request_include_fields = []
        self.task_response_include_fields = [
            'id', 'project', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'status',
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end',
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        super(TrackerTaskDisableView, self).__init__(*args, **kwargs)


class TrackerTaskDeleteView(
    TrackerTaskMixin,
    generics.RetrieveDestroyAPIView):
    """
    Delete a project task
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TaskSerializer

    def __init__(self, *args, **kwargs):
        self.task_response_include_fields = [
            'id', 'project', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'status',
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end',
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        super(TrackerTaskDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_task(instance)


class TrackerTeamCodeGenerateMixin(
    JWTPayloadMixin):
    """
    Company Project Team Code Generate Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            member = profile.get_member(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, member)
            return member
        except ObjectDoesNotExist as err:
            raise django_api_exception.TeamAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.TeamGenerateCodeSerializer
        else:
            self.serializer_class = output_serializer


class TrackerTeamMixin(
    JWTPayloadMixin):
    """
    Company Project Team Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            member = profile.get_member(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, member)
            return member
        except ObjectDoesNotExist as err:
            raise django_api_exception.TeamAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.TeamSerializer
        else:
            self.serializer_class = output_serializer


class TrackerTeamInviationListView(
    TrackerTeamMixin,
    generics.ListAPIView
):
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE)
    serializer_class = serializers.TeamSerializer

    def __init__(self, *args, **kwargs):
        self.team_response_include_fields = ['id', 'project', 'profile', 'role', 'status']
        self.project_response_include_fields = ['id', 'name', 'description', 'address', 'date_start', 'date_end',
                                                'company']
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code', 'address']
        self.profile_response_include_fields = ['id', 'first_name', 'position', 'last_name']
        super(TrackerTeamInviationListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            self.queryset = Team.objects.filter(profile=profile.id, status=0, invitation_refuse_date__isnull=True)
            return super(TrackerTeamInviationListView, self).get_queryset()
        except ObjectDoesNotExist as err:
            raise django_api_exception.ProjectAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TrackerTeamDetailView(
    TrackerTeamMixin,
    generics.RetrieveAPIView):
    """
    Get a project team member
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE)
    serializer_class = serializers.TeamSerializer

    def __init__(self, *args, **kwargs):
        self.team_response_include_fields = ['id', 'project', 'profile', 'role']
        self.project_response_include_fields = ['id', 'name', 'description', 'date_start', 'date_end', ]
        self.profile_response_include_fields = ['id', 'first_name', 'position', 'last_name']
        super(TrackerTeamDetailView, self).__init__(*args, **kwargs)


class TrackerProjectTeamAddView(
    WhistleGenericViewMixin,
    TrackerTeamMixin,
    generics.CreateAPIView):
    """
    Create a project team member
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TeamAddSerializer

    def __init__(self, *args, **kwargs):
        self.team_request_include_fields = [
            'project', 'role', 'profile'
        ]
        self.team_response_include_fields = [
            'id', 'profile', 'role', 'status'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'position',
            'email', 'phone', 'note'
        ]
        super(TrackerProjectTeamAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True

        if request.data:
            request.data['project'] = self.kwargs.get('pk', None)
        return self.create(request, *args, **kwargs)


class TrackerProjectGenerateCodeView(
    WhistleGenericViewMixin,
    TrackerTeamCodeGenerateMixin,
    generics.CreateAPIView):
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TeamGenerateCodeSerializer

    def __init__(self, *args, **kwargs):
        self.team_request_include_fields = [
            'project', 'email'
        ]
        self.team_response_include_fields = [
            'id', 'email', 'project', 'status', 'unique_code'
        ]
        super(TrackerProjectGenerateCodeView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True

        if request.data:
            request.data['project'] = self.kwargs.get('pk', None)
        return self.create(request, *args, **kwargs)


class TrackerProjectAddTeamByCodeView(
    WhistleGenericViewMixin,
    TrackerTeamCodeGenerateMixin,
    generics.CreateAPIView):
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TeamAddTeamByCodeSerializer

    def __init__(self, *args, **kwargs):
        self.team_request_include_fields = [
            'unique_code'
        ]
        self.team_response_include_fields = [
            'id', 'email', 'project', 'status', 'role', 'unique_code'
        ]
        super(TrackerProjectAddTeamByCodeView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True

        return self.create(request, *args, **kwargs)


class TrackerTeamEditView(
    WhistleGenericViewMixin,
    TrackerTeamMixin,
    generics.RetrieveUpdateAPIView):
    """
    Update a project team member
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TeamEditSerializer

    def __init__(self, *args, **kwargs):
        self.team_request_include_fields = [
            'profile', 'role', 'project'
        ]
        self.team_response_include_fields = [
            'id', 'project', 'profile', 'role', 'status'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'position',
            'email', 'phone', 'note', 'language'
        ]
        super(TrackerTeamEditView, self).__init__(*args, **kwargs)


class TrackerTeamEnableView(
    TrackerTeamMixin,
    generics.RetrieveUpdateAPIView):
    """
    Enable a project team member
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TeamEnableSerializer

    def __init__(self, *args, **kwargs):
        self.team_request_include_fields = []
        self.team_response_include_fields = ['id', 'project', 'profile', 'role']
        self.project_response_include_fields = ['id', 'name', 'description', 'date_start', 'date_end', ]
        self.profile_response_include_fields = ['id', 'first_name', 'position', 'last_name']
        super(TrackerTeamEnableView, self).__init__(*args, **kwargs)


class TrackerTeamDisableView(
    TrackerTeamMixin,
    generics.RetrieveUpdateAPIView):
    """
    Disable a project team member
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TeamDisableSerializer

    def __init__(self, *args, **kwargs):
        self.team_request_include_fields = []
        self.team_response_include_fields = ['id', 'project', 'profile', 'role', 'disabled']
        self.project_response_include_fields = ['id', 'name', 'description', 'date_start', 'date_end', ]
        self.profile_response_include_fields = ['id', 'first_name', 'position', 'last_name']
        super(TrackerTeamDisableView, self).__init__(*args, **kwargs)


class TrackerTeamDeleteView(
    TrackerTeamMixin,
    generics.RetrieveDestroyAPIView):
    """
    Delete a project team member
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TeamSerializer

    def __init__(self, *args, **kwargs):
        self.team_response_include_fields = [
            'id', 'project', 'profile', 'role'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerTeamDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        from apps.project.signals import remove_team_member_notification

        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        activity_assigned = Activity.objects.filter(workers__in=[instance.profile.id])
        for act in activity_assigned:
            act.workers.remove(instance.profile)
            act.save()
        member = profile.remove_member(instance)
        remove_team_member_notification(member._meta.model, member, instance.id)


class TrackerTaskActivityMixin(
    JWTPayloadMixin):
    """
    Company Project Task Worker Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            task = profile.get_task_activity(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, task)
            return task
        except ObjectDoesNotExist as err:
            raise django_api_exception.TaskActivityAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.TaskActivitySerializer
        else:
            self.serializer_class = output_serializer


class TrackerTaskActivityAddView(
    WhistleGenericViewMixin,
    TrackerTaskActivityMixin,
    generics.CreateAPIView):
    """
    Create a company project task activity
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TaskActivityAddSerializer

    def __init__(self, *args, **kwargs):
        self.activity_request_include_fields = [
            'task', 'workers', 'title', 'description', 'status',
            'datetime_start', 'datetime_end', 'alert',
            'starred', 'note'
        ]
        self.activity_response_include_fields = [
            'id', 'task', 'workers', 'title', 'description', 'status',
            'datetime_start', 'datetime_end', 'alert',
            'starred', 'note', 'can_assign_in_activity', 'workers_in_activity'
        ]
        self.task_response_include_fields = [
            'id', 'project', 'name', 'date_start',
            'date_end', 'date_completed', 'alert',
            'starred', 'note', 'media_set'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end',
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerTaskActivityAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True

        if request.data:
            request.data['task'] = self.kwargs.get('pk', None)
        return self.create(request, *args, **kwargs)


class TrackerTaskAttachmentAddView(
    WhistleGenericViewMixin,
    TrackerTaskMixin,
    generics.CreateAPIView):
    """
    Create a company project task activity
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TaskAttachmentAddSerializer

    def __init__(self, *args, **kwargs):
        self.task_request_include_fields = [
        ]
        self.task_response_include_fields = [
            'id', 'project', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'status', 'media_set'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end',
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        super(TrackerTaskAttachmentAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True

        if request.data:
            request.data['task'] = self.kwargs.get('pk', None)
        return self.create(request, *args, **kwargs)


class TrackerTaskAttachmentDownloadView(
    TrackerMediaAttachmentMixin, DownloadViewMixin,
    views.APIView):
    """
    Download a document
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, settings.LEVEL_2)
    file_field_name = 'media'


class TrackerTaskActivityListView(
    QuerysetMixin,
    TrackerTaskMixin,
    generics.ListAPIView):
    """
    Get all activities of a company project task
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.TaskActivitySerializer

    def __init__(self, *args, **kwargs):
        self.activity_response_include_fields = [
            'id', 'task', 'workers', 'title', 'description', 'status',
            'datetime_start', 'datetime_end', 'alert',
            'starred', 'note', 'can_assign_in_activity', 'workers_in_activity'
        ]
        self.task_response_include_fields = [
            'id', 'project', 'name', 'date_start',
            'date_end', 'date_completed', 'alert',
            'starred', 'note'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end',
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerTaskActivityListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_task_activities(self.get_object())
        return super(TrackerTaskActivityListView, self).get_queryset()


class TrackerActivityDetailView(
    TrackerTaskActivityMixin,
    generics.RetrieveAPIView):
    """
    Get a company project task activity
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TaskActivitySerializer

    def __init__(self, *args, **kwargs):
        self.activity_response_include_fields = [
            'id', 'task', 'title', 'description', 'status',
            'datetime_start', 'datetime_end', 'alert'
        ]
        self.task_response_include_fields = [
            'id', 'project', 'name', 'date_start',
            'date_end', 'date_completed'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end',
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerActivityDetailView, self).__init__(*args, **kwargs)


class TrackerActivityEditStatusView(
    WhistleGenericViewMixin,
    TrackerTaskActivityMixin,
    generics.RetrieveUpdateAPIView):
    """
    Edit a company project task activity
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TaskActivityEditSerializer

    def __init__(self, *args, **kwargs):
        self.activity_request_include_fields = [
            'status',
        ]
        self.activity_response_include_fields = [
            'id', 'task', 'profile', 'title', 'description', 'status',
            'datetime_start', 'datetime_end', 'alert'
        ]
        self.task_response_include_fields = [
            'id', 'project', 'name', 'date_start',
            'date_end', 'date_completed'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end',
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerActivityEditStatusView, self).__init__(*args, **kwargs)


class TrackerActivityEditView(
    WhistleGenericViewMixin,
    TrackerTaskActivityMixin,
    generics.RetrieveUpdateAPIView):
    """
    Edit a company project task activity
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TaskActivityEditSerializer

    def __init__(self, *args, **kwargs):
        self.activity_request_include_fields = [
            'title', 'description', 'status',
            'datetime_start', 'datetime_end',
            'alert', 'workers',
            'starred', 'note'
        ]
        self.activity_response_include_fields = [
            'id', 'task', 'workers', 'title', 'description', 'status',
            'datetime_start', 'datetime_end', 'alert',
            'starred', 'note', 'can_assign_in_activity', 'workers_in_activity'
        ]
        self.task_response_include_fields = [
            'id', 'project', 'name', 'date_start',
            'date_end', 'date_completed',
            'alert',
            'starred', 'note'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end',
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerActivityEditView, self).__init__(*args, **kwargs)


class TrackerActivityDeleteView(
    TrackerTaskActivityMixin,
    generics.RetrieveDestroyAPIView):
    """
    Delete a company project task activity
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.TaskActivitySerializer

    def __init__(self, *args, **kwargs):
        self.activity_response_include_fields = [
            'id', 'task', 'profile', 'title', 'description', 'status',
            'datetime_start', 'datetime_end', 'alert'
        ]
        self.task_response_include_fields = [
            'id', 'project', 'name', 'date_start',
            'date_end', 'date_completed'
        ]
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start',
            'date_end',
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'position', 'photo'
        ]
        super(TrackerActivityDeleteView, self).__init__(*args, **kwargs)

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_task_activity(instance)


class TrackerActivityPostAddView(
    WhistleGenericViewMixin,
    TrackerPostMixin,
    generics.CreateAPIView):
    """
    Create a Post for an activity
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, settings.LEVEL_2)
    serializer_class = serializers.ActivityPostAddSerializer

    def __init__(self, *args, **kwargs):
        self.post_request_include_fields = [
            'text', 'alert', 'is_public',
            'published_date', 'created_date', 'unique_code'
        ]
        self.activity_response_include_fields = [
            'id', 'author', 'text', 'sub_task', 'is_public',
            'published_date', 'created_date', 'unique_code', 'alert'
        ]
        self.user_response_include_fields = [
            'id', 'username',
            'email', 'first_name', 'last_name', 'is_active'
        ]
        self.profile_response_include_fields = [
            'id', 'user', 'photo', 'position',
            'company', 'role', 'email', 'first_name', 'last_name'
        ]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        super(TrackerActivityPostAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True

        if request.data:
            request.data['activity'] = self.kwargs.get('pk', None)
        return self.create(request, *args, **kwargs)


class TrackerTaskPostAddView(
    WhistleGenericViewMixin,
    TrackerPostMixin,
    generics.CreateAPIView):
    """
    Create a Post for an activity
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, settings.LEVEL_2)
    serializer_class = serializers.TaskPostAddSerializer

    def __init__(self, *args, **kwargs):
        self.post_request_include_fields = [
            'text', 'alert', 'is_public',
            'published_date', 'created_date', 'unique_code'
        ]
        self.activity_response_include_fields = [
            'id', 'author', 'text', 'task', 'sub_task', 'is_public',
            'published_date', 'created_date', 'unique_code', 'alert'
        ]
        self.user_response_include_fields = [
            'id', 'username',
            'email', 'first_name', 'last_name', 'is_active'
        ]
        self.profile_response_include_fields = [
            'id', 'user', 'photo', 'position',
            'company', 'role', 'email', 'first_name', 'last_name'
        ]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        super(TrackerTaskPostAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True

        if request.data:
            request.data['task'] = self.kwargs.get('pk', None)
        return self.create(request, *args, **kwargs)


class TrackerPostEditView(
    WhistleGenericViewMixin,
    TrackerPostEditMixin,
    generics.UpdateAPIView):
    """
    Edit a Post for an activity
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, settings.LEVEL_2)
    serializer_class = serializers.PostEditSerializer

    def __init__(self, *args, **kwargs):
        self.post_request_include_fields = [
            'text', 'alert', 'is_public',
            'published_date', 'created_date', 'unique_code'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'position',
            'role', 'email', 'fax', 'phone'
        ]
        super(TrackerPostEditView, self).__init__(*args, **kwargs)


class TrackerPostNotifyView(
    WhistleGenericViewMixin,
    TrackerPostMixin,
    generics.CreateAPIView):
    """
    Edit a Post for an activity
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, settings.LEVEL_2)
    serializer_class = serializers.PostSerializer

    def __init__(self, *args, **kwargs):
        self.post_request_include_fields = [
            'text', 'alert', 'is_public',
            'published_date', 'created_date', 'unique_code'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'position',
            'role', 'email', 'fax', 'phone'
        ]
        super(TrackerPostNotifyView, self).__init__(*args, **kwargs)


class TrackerActivityPostListView(
    WhistleGenericViewMixin,
    QuerysetMixin,
    TrackerTaskActivityMixin,
    generics.ListAPIView):
    """
    Create a Post for an activity
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.PostSerializer

    def __init__(self, *args, **kwargs):
        self.user_response_include_fields = [
            'id', 'username',
            'email', 'first_name', 'last_name', 'is_active'
        ]
        self.profile_response_include_fields = [
            'id', 'user', 'photo', 'position',
            'company', 'role', 'email', 'first_name', 'last_name'
        ]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        super(TrackerActivityPostListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_activity_posts(self.kwargs.get('pk', None))
        return super(TrackerActivityPostListView, self).get_queryset()

    def get_filters(self):
        filters = super(TrackerActivityPostListView, self).get_filters()
        if filters:
            if len(filters) != 1:
                query = []
                for key, value in enumerate(filters):
                    query.append(tuple((value, filters[value])))
                return reduce(operator.or_, [Q(x) for x in query])
        return filters


class TrackerTaskPostListView(
    WhistleGenericViewMixin,
    QuerysetMixin,
    TrackerTaskActivityMixin,
    generics.ListAPIView):
    """
    Create a Post for a task
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, settings.LEVEL_2)
    serializer_class = serializers.PostSerializer

    def __init__(self, *args, **kwargs):
        self.user_response_include_fields = [
            'id', 'username',
            'email', 'first_name', 'last_name', 'is_active'
        ]
        self.profile_response_include_fields = [
            'id', 'user', 'photo', 'position',
            'company', 'role', 'email', 'first_name', 'last_name'
        ]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        super(TrackerTaskPostListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_task_own_posts(self.kwargs.get('pk', None))
        return super(TrackerTaskPostListView, self).get_queryset()

    def get_filters(self):
        filters = super(TrackerTaskPostListView, self).get_filters()
        if filters:
            if len(filters) != 1:
                query = []
                for key, value in enumerate(filters):
                    query.append(tuple((value, filters[value])))
                return reduce(operator.or_, [Q(x) for x in query])
        return filters


class TrackerPostCommentListView(
    WhistleGenericViewMixin,
    TrackerTaskActivityMixin,
    generics.ListAPIView):
    """
    Create a Post for an activity
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.CommentSerializer

    def __init__(self, *args, **kwargs):
        self.user_response_include_fields = [
            'id', 'username',
            'email', 'first_name', 'last_name', 'is_active'
        ]
        self.profile_response_include_fields = [
            'id', 'user', 'photo', 'position',
            'company', 'role', 'email', 'first_name', 'last_name'
        ]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        super(TrackerPostCommentListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_post_comments(self.kwargs.get('pk', None))
        return super(TrackerPostCommentListView, self).get_queryset()


class TrackerCommentRepliesListView(
    WhistleGenericViewMixin,
    TrackerTaskActivityMixin,
    generics.ListAPIView):
    """
    List of comment replies
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1)
    serializer_class = serializers.CommentSerializer

    def __init__(self, *args, **kwargs):
        self.user_response_include_fields = [
            'id', 'username',
            'email', 'first_name', 'last_name', 'is_active'
        ]
        self.profile_response_include_fields = [
            'id', 'user', 'photo', 'position',
            'company', 'role', 'email', 'first_name', 'last_name'
        ]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        super(TrackerCommentRepliesListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_comment_replies(self.kwargs.get('pk', None))
        return super(TrackerCommentRepliesListView, self).get_queryset()


class TrackerCommentMixin(
    JWTPayloadMixin):
    """
    Company Project Task Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            task = profile.get_task(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, task)
            return task
        except ObjectDoesNotExist as err:
            raise django_api_exception.TaskAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.CommentSerializer
        else:
            self.serializer_class = output_serializer


class TrackerPostCommentAddView(
    WhistleGenericViewMixin,
    TrackerCommentMixin,
    generics.CreateAPIView):
    """
    Create a Comment for a Post
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, settings.LEVEL_2)
    serializer_class = serializers.PostCommentAddSerializer

    def __init__(self, *args, **kwargs):
        self.activity_request_include_fields = [
            'text', 'created_date', 'parent', 'unique_code'
        ]
        self.activity_response_include_fields = [
            'id', 'author', 'post', 'parent', 'text',
            'created_date', 'media_set', 'unique_code', 'alert'
        ]
        self.user_response_include_fields = [
            'id', 'username',
            'email', 'first_name', 'last_name', 'is_active'
        ]
        self.profile_response_include_fields = [
            'id', 'user', 'photo', 'position',
            'company', 'role', 'email', 'first_name', 'last_name'
        ]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        super(TrackerPostCommentAddView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True

        if request.data:
            request.data['post'] = self.kwargs.get('pk', None)
        return self.create(request, *args, **kwargs)


class TrackerCommentEditView(
    WhistleGenericViewMixin,
    TrackerCommentEditMixin,
    generics.UpdateAPIView):
    """
    Create a Post for an activity
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, settings.LEVEL_2)
    serializer_class = serializers.CommentEditSerializer

    def __init__(self, *args, **kwargs):
        self.comment_request_include_fields = [
            'text', 'created_date', 'unique_code'
        ]
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'position',
            'role', 'email', 'fax', 'phone'
        ]
        super(TrackerCommentEditView, self).__init__(*args, **kwargs)


class TrackerAttachmentDeleteView(
    TrackerAttachmentMixin,
    generics.RetrieveDestroyAPIView):
    """
    Delete a talk
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.TaskAttachmentAddSerializer

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_attachment(instance)


class TrackerPostDeleteView(
    TrackerPostObjectMixin,
    generics.RetrieveDestroyAPIView):
    """
    Delete a talk
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.PostSerializer

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_post(instance)


class TrackerCommentDeleteView(
    TrackerCommentObjectMixin,
    generics.RetrieveDestroyAPIView):
    """
    Delete a talk
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE,)
    serializer_class = serializers.CommentSerializer

    def perform_destroy(self, instance):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        profile.remove_comment(instance)


class TrackerSharePostToTaskMixin(
    JWTPayloadMixin):
    """
    Company Project Task Mixin
    """

    def get_object(self):
        try:
            payload = self.get_payload()
            profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
            post = profile.get_post(self.kwargs.get('pk', None))
            self.check_object_permissions(self.request, post)
            return post
        except ObjectDoesNotExist as err:
            raise django_api_exception.TaskAPIDoesNotExist(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

    def set_output_serializer(self, output_serializer=None):
        if output_serializer is None:
            self.serializer_class = serializers.SharePostToTaskSerializer
        else:
            self.serializer_class = output_serializer


class TrackerSharePostToTaskView(
    WhistleGenericViewMixin,
    TrackerSharePostToTaskMixin,
    generics.CreateAPIView):
    """
    Create a Comment for a Post
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, settings.LEVEL_2)
    serializer_class = serializers.SharePostToTaskSerializer

    def __init__(self, *args, **kwargs):
        self.post_request_include_fields = [
        ]
        self.post_response_include_fields = [
            'id', 'task', 'post', 'unique_code'
        ]
        super(TrackerSharePostToTaskView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.POST._mutable:
            request.POST._mutable = True

        if request.data:
            request.data['post'] = self.kwargs.get('pk', None)
        return self.create(request, *args, **kwargs)


class TrackerTaskPostsListView(WhistleGenericViewMixin,
                               TrackerPostMixin,
                               generics.ListAPIView):
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE)
    serializer_class = serializers.PostSerializer

    def __init__(self, *args, **kwargs):
        self.user_response_include_fields = [
            'id', 'username',
            'email', 'first_name', 'last_name', 'is_active'
        ]
        self.profile_response_include_fields = [
            'id', 'user', 'photo',
            'company', 'role', 'email', 'first_name', 'position', 'last_name'
        ]
        self.company_response_include_fields = ['id', 'name', 'slug', 'email', 'tax_code']
        super(TrackerTaskPostsListView, self).__init__(*args, **kwargs)

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_task_posts(self.kwargs.get('pk', None))
        return super(TrackerTaskPostsListView, self).get_queryset()


class TrackerProjectPhotoDownloadView(
    TrackerPhotoMixin, DownloadViewMixin,
    views.APIView):
    """
    Download a photo
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, settings.LEVEL_2,)
    file_field_name = 'photo'


class TrackerProjectVideoDownloadView(
    TrackerVideoMixin, DownloadViewMixin,
    views.APIView):
    """
    Download a photo
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = (settings.OWNER, settings.DELEGATE, settings.LEVEL_1, settings.LEVEL_2,)
    file_field_name = 'video'


# exports apis
class TrackerProjectExport(
    TrackerProjectMixin,
    QuerysetMixin,
    generics.RetrieveAPIView, generics.CreateAPIView):
    """
    Export project data
    """
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = serializers.ProjectExportSerializer

    def __init__(self, *args, **kwargs):
        self.project_response_include_fields = [
            'id', 'name', 'description', 'date_start', 'date_end',
            'company', 'referent', 'tags', 'profiles',
            'status', 'completed', 'messages_count', 'creator',
            'date_create', 'date_last_modify', 'typology',
            'shared_project', 'date_create', 'note', 'logo', 'talks', 'tasks', 'address'
        ]
        self.task_response_include_fields = [
            'id', 'name', 'assigned_company', 'date_start',
            'date_end', 'date_completed', 'progress', 'activities', 'post_set'
        ]
        self.activity_response_include_fields = [
            'id', 'title', 'description', 'status',
            'datetime_start', 'datetime_end', 'alert', 'can_assign_in_activity', 'workers_in_activity', 'post_set'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.talk_response_include_fields = ['id', 'code', 'content_type_name']
        self.profile_response_include_fields = [
            'id', 'first_name', 'last_name', 'photo', 'position',
            'role', 'email', 'fax', 'phone', 'company'
        ]
        self.company_response_include_fields = [
            'id', 'name', 'slug', 'email', 'tax_code', 'logo'
        ]
        self.user_response_include_fields = [
            'id', 'first_name', 'last_name'
        ]
        super(TrackerProjectExport, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        params = request.query_params
        response = super().retrieve(request, *args, **kwargs)
        data = response.data
        tasks = data['tasks']
        profile = self.get_profile()
        data['requested_from'] = {
            'pk': profile.pk,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'company': profile.company.name
        }
        profiles = data['profiles']
        company_profiles = {}
        for new_profile in profiles:
            if new_profile['company']['name'] in company_profiles:
                company_profiles[new_profile['company']['name']].append(new_profile)
            else:
                company_profiles[new_profile['company']['name']] = [new_profile['company']]
                company_profiles[new_profile['company']['name']].append(new_profile)

        data['company_profiles'] = company_profiles
        zip_subdir = "Report_" + str(datetime.now())
        zip_filename = "%s.zip" % zip_subdir
        # Open StringIO to grab in-memory ZIP contents
        s = BytesIO()
        zf = zipfile.ZipFile(s, "w")

        if 'type' in params and params.get('type') == 'zip':
            for task in tasks:
                filenames = []
                # get task medias
                task_mediass = MediaAssignment.objects.filter(task=task['id'])
                for media in task_mediass:
                    media_url = media.media.url
                    filenames.append(BASE_DIR + media_url)
                # get task posts medias
                for post in task['post_set']:
                    post_mediass = MediaAssignment.objects.filter(post=post['id'])
                    for media in post_mediass:
                        media_url = media.media.url
                        filenames.append(BASE_DIR + media_url)
                    # get task post comments medias
                    for comment in post['comment_set']:
                        comment_mediass = MediaAssignment.objects.filter(comment=comment['id'])
                        for media in comment_mediass:
                            media_url = media.media.url
                            filenames.append(BASE_DIR + media_url)
                        # get task post comment replies medias
                        for reply in comment['replies_set']:
                            reply_mediass = MediaAssignment.objects.filter(comment=reply['id'])
                            for media in reply_mediass:
                                media_url = media.media.url
                                filenames.append(BASE_DIR + media_url)
                # get activity medias
                for activity in task['activities']:
                    activity_mediass = MediaAssignment.objects.filter(activity=activity['id'])
                    for media in activity_mediass:
                        media_url = media.media.url
                        filenames.append(BASE_DIR + media_url)
                    # get activity posts medias
                    for post in activity['post_set']:
                        post_mediass = MediaAssignment.objects.filter(post=post['id'])
                        for media in post_mediass:
                            media_url = media.media.url
                            filenames.append(BASE_DIR + media_url)
                        # get activity post comments medias
                        for comment in post['comment_set']:
                            comment_mediass = MediaAssignment.objects.filter(comment=comment['id'])
                            for media in comment_mediass:
                                media_url = media.media.url
                                filenames.append(BASE_DIR + media_url)
                            # get activity post comment replies medias
                            for reply in comment['replies_set']:
                                reply_mediass = MediaAssignment.objects.filter(comment=reply['id'])
                                for media in reply_mediass:
                                    media_url = media.media.url
                                    filenames.append(BASE_DIR + media_url)

                for fpath in filenames:
                    fdir, fname = os.path.split(fpath)
                    zip_path = os.path.join(zip_subdir, "Task: " + task['name'], fname)
                    # Add file, at correct path
                    zf.write(fpath, zip_path)

            html_message = render_to_string('project/project/export/ProjectReport.html', data)
            zf.close()
            protocol = request.is_secure()
            if protocol:
                protocol = 'https://'
            else:
                protocol = 'http://'
            host = request.get_host()
            url = protocol + host
            generate_pdf_report.delay(html_message, {'pk': self.get_profile().pk, 'email': self.get_profile().email,
                                                     'first_name': self.get_profile().first_name,
                                                     'last_name': self.get_profile().last_name,
                                                     'project_name': data['name']}, url)
            resp = Response(data=_("We are generating your report, download will start when process is finished."),
                            status=status.HTTP_201_CREATED)
            # resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
            # resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
            return resp
        return response
