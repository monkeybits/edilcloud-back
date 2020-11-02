from rest_framework import status, generics
from rest_framework.response import Response

from apps.project.api.frontend.serializers import ProjectSerializer, ProjectGenericSerializer, TaskSerializer, \
    TaskWithActivitiesSerializer
from web import settings
from web.api.permissions import RoleAccessPermission
from web.api.views import JWTPayloadMixin, QuerysetMixin
from .. import serializers


class TrackerProjectsListView(
    JWTPayloadMixin,
    QuerysetMixin,
    generics.ListAPIView):
    permission_classes = (RoleAccessPermission,)
    permission_roles = settings.MEMBERS
    serializer_class = ProjectGenericSerializer

    def get_queryset(self):
        payload = self.get_payload()
        profile = self.request.user.get_profile_by_id(payload['extra']['profile']['id'])
        self.queryset = profile.list_projects()
        return super(TrackerProjectsListView, self).get_queryset()

    def list(self, request, *args, **kwargs):
        #project_serializer = self.serializer_class(self.get_queryset(), many=True)
        projects = self.get_queryset()
        tasks_list = []
        activities_list = []
        for project in projects:
            for task in project.tasks.all():
                tasks_list.append({
                    'id': task.id,
                    'name': task.name,
                    'date_start': task.date_start,
                    'date_end': task.date_end,
                    'date_completed': task.date_completed,
                    'progress': task.progress,
                    'alert': task.alert,
                    'note': task.note,
                    'type': 'task'
                })
                for activity in task.activities.all():
                    activities_list.append({
                        'id': activity.id,
                        'title': activity.title,
                        'description': activity.description,
                        'status': activity.status,
                        'datetime_start': activity.datetime_start,
                        'datetime_end': activity.datetime_end,
                        'alert': activity.alert,
                        'note': activity.note,
                        'type': 'activity'

                    })
        tot_list = tasks_list + activities_list
        if 'type' in request.query_params:
            type = request.query_params.get('type')
            if type == 'task':
                tot_list = tasks_list
            elif type == 'activity':
                tot_list = activities_list
            else:
                tot_list = tot_list

        return Response(data=tot_list, status=status.HTTP_200_OK)

