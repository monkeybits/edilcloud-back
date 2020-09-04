# -*- coding: utf-8 -*-
import datetime
import random

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers, status

from apps.message.api.frontend.serializers import TalkSerializer
from apps.profile.api.frontend.serializers import ProfileSerializer, UserSerializer
from ... import models
from apps.profile.api.frontend import serializers as profile_serializers
from apps.document.api.frontend import serializers as document_serializers
from web import exceptions as django_exception
from web.drf import exceptions as django_api_exception
from web.api.views import JWTPayloadMixin, daterange, get_first_last_dates_of_month_and_year
from web.api.serializers import DynamicFieldsModelSerializer
from ...models import ProjectCompanyColorAssignment, Comment

palette_color = [
    '#d32f2f'
    '#7b1fa2'
    '#303f9f'
    '#00796b'
    '#00e5ff'
    '#1b5e20'
    '#76ff03'
    '#ffeb3b'
    '#ff6f00'
    '#795548'
    '#212121'
    '#ff4081'
]
palette_color2 = [
'#F44336',
  '#FFEBEE',
  '#FFCDD2',
  '#EF9A9A',
  '#E57373',
  '#EF5350',
  '#F44336',
  '#E53935',
  '#D32F2F',
  '#C62828',
  '#B71C1C',
  '#FF8A80',
  '#FF5252',
  '#FF1744',
  '#D50000',
  '#E91E63',
  '#FCE4EC',
  '#F8BBD0',
  '#F48FB1',
  '#F06292',
  '#EC407A',
  '#E91E63',
  '#D81B60',
  '#C2185B',
  '#AD1457',
  '#880E4F',
  '#FF80AB',
  '#FF4081',
  '#F50057',
  '#C51162',
  '#9C27B0',
  '#F3E5F5',
  '#E1BEE7',
  '#CE93D8',
  '#BA68C8',
  '#AB47BC',
  '#9C27B0',
  '#8E24AA',
  '#7B1FA2',
  '#6A1B9A',
  '#4A148C',
  '#EA80FC',
  '#E040FB',
  '#D500F9',
  '#AA00FF',
  '#673AB7',
  '#EDE7F6',
  '#D1C4E9',
  '#B39DDB',
  '#9575CD',
  '#7E57C2',
  '#673AB7',
  '#5E35B1',
  '#512DA8',
  '#4527A0',
  '#311B92',
  '#B388FF',
  '#7C4DFF',
  '#651FFF',
  '#6200EA',
  '#3F51B5',
  '#E8EAF6',
  '#C5CAE9',
  '#9FA8DA',
  '#7986CB',
  '#5C6BC0',
  '#3F51B5',
  '#3949AB',
  '#303F9F',
  '#283593',
  '#1A237E',
  '#8C9EFF',
  '#536DFE',
  '#3D5AFE',
  '#304FFE',
  '#2196F3',
  '#E3F2FD',
  '#BBDEFB',
  '#90CAF9',
  '#64B5F6',
  '#42A5F5',
  '#2196F3',
  '#1E88E5',
  '#1976D2',
  '#1565C0',
  '#0D47A1',
  '#82B1FF',
  '#448AFF',
  '#2979FF',
  '#2962FF',
  '#03A9F4',
  '#E1F5FE',
  '#B3E5FC',
  '#81D4FA',
  '#4FC3F7',
  '#29B6F6',
  '#03A9F4',
  '#039BE5',
  '#0288D1',
  '#0277BD',
  '#01579B',
  '#80D8FF',
  '#40C4FF',
  '#00B0FF',
  '#0091EA',
  '#00BCD4',
  '#E0F7FA',
  '#B2EBF2',
  '#80DEEA',
  '#4DD0E1',
  '#26C6DA',
  '#00BCD4',
  '#00ACC1',
  '#0097A7',
  '#00838F',
  '#006064',
  '#84FFFF',
  '#18FFFF',
  '#00E5FF',
  '#00B8D4',
  '#009688',
  '#E0F2F1',
  '#B2DFDB',
  '#80CBC4',
  '#4DB6AC',
  '#26A69A',
  '#009688',
  '#00897B',
  '#00796B',
  '#00695C',
  '#004D40',
  '#A7FFEB',
  '#64FFDA',
  '#1DE9B6',
  '#00BFA5',
  '#4CAF50',
  '#E8F5E9',
  '#C8E6C9',
  '#A5D6A7',
  '#81C784',
  '#66BB6A',
  '#4CAF50',
  '#43A047',
  '#388E3C',
  '#2E7D32',
  '#1B5E20',
  '#B9F6CA',
  '#69F0AE',
  '#00E676',
  '#00C853',
  '#8BC34A',
  '#F1F8E9',
  '#DCEDC8',
  '#C5E1A5',
  '#AED581',
  '#9CCC65',
  '#8BC34A',
  '#7CB342',
  '#689F38',
  '#558B2F',
  '#33691E',
  '#CCFF90',
  '#B2FF59',
  '#76FF03',
  '#64DD17',
  '#CDDC39',
  '#F9FBE7',
  '#F0F4C3',
  '#E6EE9C',
  '#DCE775',
  '#D4E157',
  '#CDDC39',
  '#C0CA33',
  '#AFB42B',
  '#9E9D24',
  '#827717',
  '#F4FF81',
  '#EEFF41',
  '#C6FF00',
  '#AEEA00',
  '#FFEB3B',
  '#FFFDE7',
  '#FFF9C4',
  '#FFF59D',
  '#FFF176',
  '#FFEE58',
  '#FFEB3B',
  '#FDD835',
  '#FBC02D',
  '#F9A825',
  '#F57F17',
  '#FFFF8D',
  '#FFFF00',
  '#FFEA00',
  '#FFD600',
  '#FFC107',
  '#FFF8E1',
  '#FFECB3',
  '#FFE082',
  '#FFD54F',
  '#FFCA28',
  '#FFC107',
  '#FFB300',
  '#FFA000',
  '#FF8F00',
  '#FF6F00',
  '#FFE57F',
  '#FFD740',
  '#FFC400',
  '#FFAB00',
  '#FF9800',
  '#FFF3E0',
  '#FFE0B2',
  '#FFCC80',
  '#FFB74D',
  '#FFA726',
  '#FF9800',
  '#FB8C00',
  '#F57C00',
  '#EF6C00',
  '#E65100',
  '#FFD180',
  '#FFAB40',
  '#FF9100',
  '#FF6D00',
  '#FF5722',
  '#FBE9E7',
  '#FFCCBC',
  '#FFAB91',
  '#FF8A65',
  '#FF7043',
  '#FF5722',
  '#F4511E',
  '#E64A19',
  '#D84315',
  '#BF360C',
  '#FF9E80',
  '#FF6E40',
  '#FF3D00',
  '#DD2C00',
  '#795548',
  '#EFEBE9',
  '#D7CCC8',
  '#BCAAA4',
  '#A1887F',
  '#8D6E63',
  '#795548',
  '#6D4C41',
  '#5D4037',
  '#4E342E',
  '#3E2723',
  '#9E9E9E',
  '#FAFAFA',
  '#F5F5F5',
  '#EEEEEE',
  '#E0E0E0',
  '#BDBDBD',
  '#9E9E9E',
  '#757575',
  '#616161',
  '#424242',
  '#212121',
  '#607D8B',
  '#ECEFF1',
  '#CFD8DC',
  '#B0BEC5',
  '#90A4AE',
  '#78909C',
  '#607D8B',
  '#546E7A',
  '#455A64',
  '#37474F',
  '#263238',
  '#000000',
  '#FFFFFF',
]

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
    messages_count = serializers.ReadOnlyField(source='get_messages_count')
    days_for_gantt = serializers.SerializerMethodField(source='get_days_for_gantt')
    project_owner = profile_serializers.CompanySerializer(source='get_project_owner')
    company = profile_serializers.CompanySerializer()
    referent = profile_serializers.ProfileSerializer()
    profiles = profile_serializers.ProfileSerializer(many=True)
    talks = TalkSerializer(many=True)
    creator = profile_serializers.UserSerializer()
    last_message_created = serializers.SerializerMethodField()

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
    def get_last_message_created(self, obj):
        talk = obj.talks.last()
        if talk:
            return talk.messages.all().last().date_create
        else:
            None


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
            ProjectCompanyColorAssignment.objects.create(
                project=project, company=project.company, color=choose_random_color(project.company, project)
            )
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
    only_read = serializers.SerializerMethodField()

    class Meta:
        model = models.Task
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        view = self.get_view
        if view:
            return view.task_response_include_fields
        return super(TaskSerializer, self).get_field_names(*args, **kwargs)

    def get_only_read(self, obj):
        payload = self.context['view'].get_payload()
        profile = self.context['request'].user.get_profile_by_id(payload['extra']['profile']['id'])
        if obj.project.company == profile.company or obj.assigned_company == profile.company:
            return False
        else:
            return True

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


class FilteredListSerializer(serializers.ListSerializer):
    """Serializer to filter the active system, which is a boolen field in
       System Model. The value argument to to_representation() method is
      the model instance"""

    def to_representation(self, data):
        if type(data) is not list:
            data = data.filter(parent__isnull=True)
        return super(FilteredListSerializer, self).to_representation(data)


class CommentSerializer(DynamicFieldsModelSerializer, JWTPayloadMixin, serializers.ModelSerializer):
    author = ProfileSerializer()
    replies_set = serializers.SerializerMethodField()

    class Meta:
        model = models.Comment
        list_serializer_class = FilteredListSerializer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            payload = self.get_payload()
            self.profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])

    def get_replies_set(self, obj):
        comments_list = []
        comments = Comment.objects.filter(parent=obj.id)
        for comment in comments:
            try:
                photo_url = comment.author.photo.url
                protocol = self.context['request'].is_secure()
                if protocol:
                    protocol = 'https://'
                else:
                    protocol = 'http://'
                host = self.context['request'].get_host()
                author_photo = protocol + host + photo_url
            except:
                author_photo = None
            comments_list.append(
                {
                    'id': comment.id,
                    'text': comment.text,
                    'author': {
                        'id': comment.author.id,
                        'user': {
                            'id': comment.author.user.id,
                            'username': comment.author.user.username,
                            "first_name": comment.author.user.first_name,
                            "last_name": comment.author.user.last_name
                        },
                        "photo": author_photo,
                        "first_name": comment.author.first_name,
                        "last_name": comment.author.last_name
                    },
                    'created_date': comment.created_date,
                    'parent': comment.parent.id if comment.parent is not None else None
                }
            )
        return comments_list

class PostSerializer(DynamicFieldsModelSerializer, JWTPayloadMixin, serializers.ModelSerializer):
    comment_set = CommentSerializer(many=True)
    author = ProfileSerializer()

    class Meta:
        model = models.Post
        fields = [
            'id',
            'author',
            'published_date',
            'sub_task',
            'task',
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
        comments = obj.comment_set.all().order_by('-created_by')
        comments_list = []
        for comment in comments:
            serializer = CommentSerializer(data=comment)
            if serializer.is_valid():
                comments_list.append(serializer.data)
        return comments_list

def choose_random_color(company, project):
    old_pal = []
    for pr in ProjectCompanyColorAssignment.objects.filter(company=company, project=project):
        old_pal.append(pr.color)

    while True:
        random_color = random.choice(palette_color)
        if random_color in old_pal:
            pass
        else:
            break
    if random_color == '':
        while True:
            random_color = random.choice(palette_color2)
            if random_color in old_pal:
                pass
            else:
                break
    return random_color

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
            is_external = self.context['request'].query_params.get('is_external')
            if is_external.lower() == 'true':
                # add company with invitation
                validated_data['project_invitation_date'] = datetime.datetime.now()
                validated_data['status'] = 0
                member = self.profile.create_member(validated_data)
                if not ProjectCompanyColorAssignment.objects.filter(project=member.project, company=self.profile.company).exists():
                    ProjectCompanyColorAssignment.objects.create(
                        project=member.project, company=self.profile.company, color=choose_random_color(self.profile.company, member.project)
                    )
                return member
            else:
                # don't invite but add without invitation
                validated_data['project_invitation_date'] = datetime.datetime.now()
                validated_data['status'] = 1
                member = self.profile.create_member(validated_data)
                if not ProjectCompanyColorAssignment.objects.filter(project=member.project, company=self.profile.company).exists():
                    ProjectCompanyColorAssignment.objects.create(
                        project=member.project, company=self.profile.company, color=choose_random_color(self.profile.company, member.project)
                    )
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

class TaskPostAddSerializer(
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
        return super(TaskPostAddSerializer, self).get_field_names(*args, **kwargs)

    def create(self, validated_data):
        try:
            validated_data['author'] = self.author
            validated_data['task'] = self.request.data['task']
            files = list(self.request.FILES.values())
            activity_post = self.author.create_task_post(validated_data)
            return activity_post
        except ObjectDoesNotExist as err:
            raise django_api_exception.TaskActivityAddAPIPermissionDenied(
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