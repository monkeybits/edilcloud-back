# -*- coding: utf-8 -*-
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers, status

from ... import models
from apps.profile.api.frontend import serializers as profile_serializers
from apps.document.api.frontend import serializers as document_serializers
from web import exceptions as django_exception
from web.drf import exceptions as django_api_exception
from web.api.views import JWTPayloadMixin, daterange, get_first_last_dates_of_month_and_year
from web.api.serializers import DynamicFieldsModelSerializer


class ProjectGenericSerializer(
    DynamicFieldsModelSerializer):
    typology = serializers.ReadOnlyField(source='get_typology')
    completed = serializers.ReadOnlyField(source='get_completed_perc')
    shared_companies = serializers.ReadOnlyField(source='get_shared_companies')
    task_companies = profile_serializers.CompanySerializer(source='get_shared_companies_qs', many=True)
    messages_count = serializers.ReadOnlyField(source='get_messages_count')
    company = profile_serializers.CompanySerializer()

    class Meta:
        model = models.Project
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.project_response_include_fields
        return super(ProjectGenericSerializer, self).get_field_names(*args, **kwargs)


class ProjectSerializer(
    DynamicFieldsModelSerializer):
    typology = serializers.ReadOnlyField(source='get_typology')
    completed = serializers.ReadOnlyField(source='get_completed_perc')
    shared_companies = serializers.ReadOnlyField(source='get_shared_companies')
    task_companies = profile_serializers.CompanySerializer(source='get_shared_companies_qs', many=True)
    messages_count = serializers.ReadOnlyField(source='get_messages_count')
    days_for_gantt = serializers.SerializerMethodField(source='get_days_for_gantt')
    project_owner = profile_serializers.CompanySerializer(source='get_project_owner')
    company = profile_serializers.CompanySerializer()
    referent = profile_serializers.ProfileSerializer()
    profiles = profile_serializers.ProfileSerializer(many=True)
    creator = profile_serializers.UserSerializer()
    shared_project = ProjectGenericSerializer()

    class Meta:
        model = models.Project
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            if 'month' in view.kwargs: self.month = view.kwargs['month']
            if 'year' in view.kwargs: self.year = view.kwargs['year']
            return view.project_response_include_fields
        return super(ProjectSerializer, self).get_field_names(*args, **kwargs)

    def get_days_for_gantt(self, obj):
        days = []
        date_from, date_to = get_first_last_dates_of_month_and_year(self.month, self.year)

        start_date, end_date = (date_from, date_to)
        if obj.date_start.month == date_from.month: start_date = obj.date_start
        if obj.date_end.month == date_from.month: end_date = obj.date_end
        for dt in daterange(start_date, end_date):
            days.append(dt.day)
        return days


class SimpleProjectSerializer(
    DynamicFieldsModelSerializer):
    class Meta:
        model = models.Project
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            if 'month' in view.kwargs: self.month = view.kwargs['month']
            if 'year' in view.kwargs: self.year = view.kwargs['year']
            return view.project_response_include_fields
        return super(SimpleProjectSerializer, self).get_field_names(*args, **kwargs)


class ProjectCalendarSerializer(
    DynamicFieldsModelSerializer):
    start = serializers.DateField(source='date_start')
    end = serializers.DateField(source='date_end')
    title = serializers.CharField(source='name')

    class Meta:
        model = models.Project
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.project_response_include_fields
        return super(ProjectCalendarSerializer, self).get_field_names(*args, **kwargs)


class ProjectAddSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin):
    class Meta:
        model = models.Project
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
            return view.project_request_include_fields
        return super(ProjectAddSerializer, self).get_field_names(*args, **kwargs)

    def validate(self, attrs):
        if 'date_start' in attrs and 'date_end' in attrs:
            if attrs['date_start'] > attrs['date_end']:
                raise serializers.ValidationError(
                    {'date_end': _('EndDate should be greater than StartDate')}
                )
        return attrs

    def create(self, validated_data):
        try:
            project = self.profile.create_project(validated_data)
            return project
        except Exception as exc:
            if type(exc).__name__ == 'ValidationError':
                raise serializers.ValidationError(
                    {'name': ['Name should be unique']}
                )


class ProjectEditSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):
    class Meta:
        model = models.Project
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
            return view.project_request_include_fields
        return super(ProjectEditSerializer, self).get_field_names(*args, **kwargs)

    def validate(self, attrs):
        if 'date_start' in attrs and 'date_end' in attrs:
            if attrs['date_start'] > attrs['date_end']:
                raise serializers.ValidationError(
                    {'date_end': _('EndDate should be greater than StartDate')}
                )
        return attrs

    def update(self, instance, validated_data):
        validated_data['id'] = instance.id
        project = self.profile.edit_project(validated_data)
        return project


class ProjectEnableSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            request = kwargs['context']['request']
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.project_request_include_fields
        return super(ProjectEnableSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        project = self.profile.enable_project(instance)
        return project


class ProjectDisableSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):
    class Meta:
        model = models.Project
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
            return view.project_request_include_fields
        return super(ProjectDisableSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        project = self.profile.disable_project(instance)
        return project


class TaskGenericSerializer(
    DynamicFieldsModelSerializer):
    share_status = serializers.ReadOnlyField(source="get_share_status")

    class Meta:
        model = models.Task
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.task_response_include_fields
        return super(TaskGenericSerializer, self).get_field_names(*args, **kwargs)


class TaskSerializer(
    DynamicFieldsModelSerializer):
    project = ProjectSerializer()
    assigned_company = profile_serializers.CompanySerializer()
    workers = profile_serializers.ProfileSerializer(many=True)
    share_status = serializers.ReadOnlyField(source="get_share_status")
    shared_task = TaskGenericSerializer()

    class Meta:
        model = models.Task
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.task_response_include_fields
        return super(TaskSerializer, self).get_field_names(*args, **kwargs)


class TaskAddSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):
    class Meta:
        model = models.Task
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
            return view.task_request_include_fields
        return super(TaskAddSerializer, self).get_field_names(*args, **kwargs)

    def validate(self, attrs):
        if 'date_start' in attrs and 'date_end' in attrs:
            if attrs['date_start'] > attrs['date_end']:
                raise serializers.ValidationError('EndDate should be greater than StartDate')
        return attrs

    def create(self, validated_data):
        task = self.profile.create_task(validated_data)
        return task


class TaskEditSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin):
    class Meta:
        model = models.Task
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
            return view.task_request_include_fields
        return super(TaskEditSerializer, self).get_field_names(*args, **kwargs)

    def validate(self, attrs):
        if 'date_start' in attrs and 'date_end' in attrs:
            if attrs['date_start'] > attrs['date_end']:
                raise serializers.ValidationError('EndDate should be greater than StartDate')
        return attrs

    def update(self, instance, validated_data):
        validated_data['id'] = instance.id
        if (not instance.assigned_company) and validated_data['assigned_company']:
            task = self.profile.assign_task(validated_data)
        else:
            task = self.profile.edit_task(validated_data)
        return task


class TaskEnableSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):
    class Meta:
        model = models.Task
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
            return view.task_request_include_fields
        return super(TaskEnableSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        task = self.profile.enable_task(instance)
        return task


class TaskDisableSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):
    class Meta:
        model = models.Task
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
            return view.task_request_include_fields
        return super(TaskDisableSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        task = self.profile.disable_task(instance)
        return task


class TeamSerializer(
    DynamicFieldsModelSerializer):
    role = serializers.ReadOnlyField(source="get_role")
    project = ProjectSerializer()
    profile = profile_serializers.ProfileSerializer()

    class Meta:
        model = models.Team
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.team_response_include_fields
        return super(TeamSerializer, self).get_field_names(*args, **kwargs)


class CommentSerializer(DynamicFieldsModelSerializer, JWTPayloadMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])


class PostSerializer(DynamicFieldsModelSerializer, JWTPayloadMixin, serializers.ModelSerializer):
    comment_set = CommentSerializer(many=True)

    class Meta:
        model = models.Post
        fields = [
            'id',
            'author',
            'published_date',
            'sub_task',
            'media',
            'text',
            'comment_set'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_comments(self, obj):
        comments = obj.comment_set.all()
        comments_list = []
        for comment in comments:
            serializer = CommentSerializer(data=comment)
            if serializer.is_valid():
                comments_list.append(serializer.data)
        return comments_list


class TeamAddSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):
    class Meta:
        model = models.Team
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
            return view.team_request_include_fields
        return super(TeamAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        try:
            member = self.profile.create_member(validated_data)
            return member
        except django_exception.ProjectMemberAddPermissionDenied as err:
            raise django_api_exception.ProjectMemberAddAPIPermissionDenied(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TeamEditSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):
    class Meta:
        model = models.Team
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
            return view.team_request_include_fields
        return super(TeamEditSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        validated_data['id'] = instance.id
        member = self.profile.edit_member(validated_data)
        return member


class TeamEnableSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):
    class Meta:
        model = models.Team
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
            return view.team_request_include_fields
        return super(TeamEnableSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        member = self.profile.enable_member(instance)
        return member


class TeamDisableSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):
    class Meta:
        model = models.Team
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
            return view.team_request_include_fields
        return super(TeamDisableSerializer, self).get_field_names(*args, **kwargs)

    def update(self, instance, validated_data):
        member = self.profile.disable_member(instance)
        return member


class TaskActivitySerializer(
    DynamicFieldsModelSerializer):
    task = TaskSerializer()
    profile = profile_serializers.ProfileSerializer()
    days_for_gantt = serializers.SerializerMethodField(source='get_days_for_gantt')

    class Meta:
        model = models.Activity
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            if 'month' in view.kwargs: self.month = view.kwargs['month']
            if 'year' in view.kwargs: self.year = view.kwargs['year']
            return view.activity_response_include_fields
        return super(TaskActivitySerializer, self).get_field_names(*args, **kwargs)

    def get_days_for_gantt(self, obj):
        days = []
        date_from, date_to = get_first_last_dates_of_month_and_year(self.month, self.year)

        start_date, end_date = (date_from, date_to)
        if obj.datetime_start.month == date_from.month: start_date = obj.datetime_start
        if obj.datetime_end.month == date_from.month: end_date = obj.datetime_end

        if isinstance(start_date, datetime.datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime.datetime):
            end_date = end_date.date()
        for dt in daterange(start_date, end_date):
            days.append(dt.day)
        return days


class TaskActivityAddSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):
    class Meta:
        model = models.Activity
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
            return view.activity_request_include_fields
        return super(TaskActivityAddSerializer, self).get_field_names(*args, **kwargs)

    def validate(self, attrs):
        if 'datetime_start' in attrs and 'datetime_end' in attrs:
            if attrs['datetime_start'] > attrs['datetime_end']:
                raise serializers.ValidationError('EndDateTime should be greater than StartDateTime')
        return attrs

    def create(self, validated_data):
        try:
            task_activity = self.profile.create_task_activity(validated_data)
            return task_activity
        except ObjectDoesNotExist as err:
            raise django_api_exception.TaskActivityAddAPIPermissionDenied(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class TaskActivityEditSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):
    class Meta:
        model = models.Activity
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
            return view.activity_request_include_fields
        return super(TaskActivityEditSerializer, self).get_field_names(*args, **kwargs)

    def validate(self, attrs):
        if 'datetime_start' in attrs and 'datetime_end' in attrs:
            if attrs['datetime_start'] > attrs['datetime_end']:
                raise serializers.ValidationError('EndDateTime should be greater than StartDateTime')
        return attrs

    def update(self, instance, validated_data):
        try:
            validated_data['id'] = instance.id
            task_activity = self.profile.edit_task_activity(validated_data)
            return task_activity
        except ObjectDoesNotExist as err:
            raise django_api_exception.TaskActivityEditAPIPermissionDenied(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class ActivityPostAddSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):
    class Meta:
        model = models.Post
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.author = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.activity_request_include_fields
        return super(ActivityPostAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        try:
            validated_data['author'] = self.author
            validated_data['activity'] = self.request.data['activity']
            files = list(self.request.FILES.values())
            activity_post = self.author.create_activity_post(validated_data)
            return activity_post
        except ObjectDoesNotExist as err:
            raise django_api_exception.TaskActivityAddAPIPermissionDenied(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )


class PostCommentAddSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.author = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.activity_request_include_fields
        return super(PostCommentAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        try:
            validated_data['author'] = self.author
            validated_data['post'] = self.request.data['post']
            comment_parent = validated_data['parent']
            if comment_parent != None:
                if comment_parent.parent != None:
                    raise serializers.ValidationError(
                        {'parent': _('Cannot assign to a parent that already have a parent')}
                    )
            post_comment = self.author.create_post_comment(validated_data)
            return post_comment
        except ObjectDoesNotExist as err:
            raise django_api_exception.TaskActivityAddAPIPermissionDenied(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

class SharePostToTaskSerializer(
    DynamicFieldsModelSerializer,
    JWTPayloadMixin,
    serializers.ModelSerializer):

    class Meta:
        model = models.TaskPostAssignment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.author = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.activity_request_include_fields
        return super(SharePostToTaskSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        try:
            validated_data['creator'] = self.author.user
            validated_data['last_modifier'] = self.author.user
            validated_data['post'] = self.request.data['post']
            post_comment = self.author.share_post(validated_data)
            return "Successfully shared to Task parent"
        except ObjectDoesNotExist as err:
            raise django_api_exception.TaskActivityAddAPIPermissionDenied(
                status.HTTP_403_FORBIDDEN, self.request, _("{}".format(err.msg if hasattr(err, 'msg') else err))
            )

# class TaskPostsListSerializer(
#     DynamicFieldsModelSerializer,
#     JWTPayloadMixin,
#     serializers.ModelSerializer):
#     class Meta:
#         models = models.Post
#         fields = '__all__'