# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import calendar
import datetime
import os
import pathlib

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import transaction
from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.template.defaultfilters import truncatechars
from django.db.models import Q, Count
from django.utils.text import slugify

from web.core.models import UserModel, DateModel, StatusModel, OrderedModel, CleanModel
from . import managers
from web import exceptions as django_exception


from django.db.models import Lookup
from django.db.models.fields import Field
from django.utils import timezone

from ..document.models import document_limit_choices_to
from ..media.models import get_upload_photo_path

import uuid

def get_upload_logo_path(instance, filename):
    media_dir = slugify(instance.name[0:2])
    ext = pathlib.Path(filename).suffix
    filename = '{}{}'.format(slugify(instance.name), ext)
    return os.path.join(u"project", u"logo", u"{0}".format(media_dir), filename)

def get_upload_post_path(instance, filename):
    last_post = Post.objects.last().pk
    return os.path.join(u"subtasks", u"{0}".format(instance.sub_task_id), u"posts", u"{0}".format(str(last_post + 1)), filename)

@Field.register_lookup
class NotEqual(Lookup):
    lookup_name = 'ne'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params


@python_2_unicode_compatible
class Project(CleanModel, UserModel, DateModel, OrderedModel):
    objects = managers.ProjectManager()
    company = models.ForeignKey(
        'profile.Company',
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name=_('company')
    )
    referent = models.ForeignKey(
        'profile.Profile',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='referent_projects',
        verbose_name=_('referent'),
    )
    shared_project = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='internal_projects',
        verbose_name=_('shared project')
    )
    profiles = models.ManyToManyField(
        'profile.Profile',
        through='Team',
        related_name='projects',
        verbose_name=_('profiles')
    )
    name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_("name"),
    )
    description = models.TextField(
        verbose_name=_('description'),
    )
    date_start = models.DateField(
        verbose_name=_('start date'),
    )
    date_end = models.DateField(
        blank=True, null=True,
        verbose_name=_('end date'),
    )
    status = models.IntegerField(
        choices=settings.PROJECT_PROJECT_STATUS_CHOICES,
        default=1,
        verbose_name=_('status'),
    )
    tags = JSONField(
        default={},
        blank=True, null=True,
        verbose_name=_('tags'),
        help_text=_('products'),
    )
    logo = models.ImageField(
        blank=True,
        upload_to=get_upload_logo_path,
        verbose_name=_('logo'),
    )
    note = models.TextField(
        blank=True,
        verbose_name=_("note"),
    )
    talks = GenericRelation(
        'message.Talk',
        blank=True, null=True,
        related_query_name='projects'
    )
    documents = GenericRelation(
        'document.Document',
        blank=True, null=True,
        related_query_name='projects'
    )
    photos = GenericRelation(
        'media.Photo',
        blank=True, null=True,
        related_query_name='projects'
    )
    videos = GenericRelation(
        'media.Video',
        blank=True, null=True,
        related_query_name='projects'
    )

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        permissions = (
            ("list_project", "can list project"),
            ("detail_project", "can detail project"),
            ("disable_project", "can disable project"),
        )
        unique_together = (
            ('company', 'name',),
        )
        ordering = ['-date_last_modify']
        get_latest_by = "date_create"

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        if self.is_generic_project:
            self.__class__ = GenericProject
        elif self.is_internal_project:
            self.__class__ = InternalProject
        elif self.is_shared_project:
            self.__class__ = SharedProject
        elif self.is_internal_shared_project:
            self.__class__ = InternalSharedProject

    def __str__(self):
        return '{}: {} - {}'.format(self.company, self.referent, self.name)

    @property
    def get_tags_count(self):
        return len(self.tags) if self.tags else 0

    @property
    def get_tasks_count(self):
        return self.tasks.count()

    get_tasks_count.fget.short_description = _('Tasks count')

    @property
    def get_tasks(self):
        return self.tasks.all()

    get_tasks.fget.short_description = _('Tasks')

    @property
    def get_shared_project_short_name(self):
        if self.shared_project:
            return truncatechars(self.shared_project, 50)
        return self.shared_project

    get_shared_project_short_name.fget.short_description = _('Shared Project')

    @property
    def get_members_count(self):
        return self.members.count()

    get_members_count.fget.short_description = _('Members')

    def get_shared_tasks(self):
        if self.typology == self.INTERNAL:
            return self.shared_project.tasks.all()
        return self.tasks.all()

    def get_talks(self):
        return self.talks.all()

    def get_photos(self):
        return self.photos.all()

    def get_videos(self):
        return self.videos.all()

    def create_team(self, team_dict):
        team = Team(
            project=self,
            **team_dict
        )
        team.save()
        return team

    def create_task(self, task_dict):
        task = Task(
            project=self,
            **task_dict
        )
        task.save()
        return task

    # @property
    # def is_internal_project(self):
    #     projects = Project.objects.filter(tasks__isnull=False).filter(
    #         tasks__assigned_company=self.company).annotate(
    #         tasks__assigned_company__count=Count('tasks__assigned_company', distinct=True)).filter(
    #         tasks__assigned_company__count=1)
    #     return True if projects else False
    #
    # @property
    # def is_shared_project(self):
    #     projects = Project.objects.filter(
    #         tasks__isnull=False).exclude(tasks__assigned_company=self.company)
    #     return True if projects else False
    #
    # @property
    # def is_internal_shared_project(self):
    #     projects = Project.objects.filter(tasks__isnull=False).filter(
    #         tasks__assigned_company=self.company).annotate(
    #         tasks__assigned_company__count=Count('tasks__assigned_company', distinct=True)).filter(
    #         tasks__assigned_company__count__gt=1)
    #     return True if projects else False

    @property
    def is_internal_project(self):
        return True if self.tasks.exclude(
            assigned_company=self.company).count() == 0 else False

    @property
    def is_shared_project(self):
        companies = self.tasks.filter(assigned_company=self.company).count()
        external_companies = self.tasks.exclude(assigned_company=self.company).count()
        return True if companies == 0 and external_companies != 0 else False

    @property
    def is_internal_shared_project(self):
        companies = self.tasks.filter(assigned_company=self.company).count()
        external_companies = self.tasks.exclude(assigned_company=self.company).count()
        return True if companies != 0 and external_companies != 0 else False

    @property
    def is_generic_project(self):
        return True if self.tasks.count() == 0 else False

    def get_completed_perc(self):
        # Todo: Improve percentage calculation
        total_percentage = 0
        total_duration = 0
        for task in self.tasks.all():
            total_percentage += task.progress_with_duration()
            total_duration += task.duration()
        if total_duration == 0 & total_percentage == 0:
            return 0
        return "%.0f" % (total_percentage/total_duration)

    def get_typology(self):
        if self.is_generic_project:
            return 'g'
        elif self.is_internal_project:
            return 'i'
        elif self.is_shared_project:
            return 's'
        elif self.is_internal_shared_project:
            return 'is'

    def get_shared_companies(self):
        return self.tasks.exclude(assigned_company__isnull=True).exclude(
            assigned_company=self.company
        ).values('assigned_company__id', 'assigned_company__name', 'assigned_company__logo')
        # return Project.objects.filter(
        #     shared_project=self
        # ).values('company__id', 'company__name', 'company__logo')

    def get_shared_companies_qs(self):
        from apps.profile.models import Company
        companies = Company.objects.filter(assigned_tasks__project=self).exclude(
            id=self.company.id
        )
        return companies

    @property
    def get_messages_count(self):
        # Todo: Optimize the following code
        total_messages = 0
        for talk in self.talks.all():
            total_messages += talk.get_messages_count
        return total_messages

    @property
    def get_project_owner(self):
        if self.shared_project:
            return self.shared_project.company
        return self.company


@python_2_unicode_compatible
class InternalProject(Project):
    objects = managers.InternalProjectManager()

    class Meta:
        proxy = True
        verbose_name = _('internal project')
        verbose_name_plural = _('internal projects')
        permissions = (
            ("list_internalproject", "can list internal project"),
            ("detail_internalproject", "can detail internal project"),
            ("disable_internalproject", "can disable internal project"),
        )

    def __str__(self):
        return '{}: {} - {}'.format(self.company, self.referent, self.name)


@python_2_unicode_compatible
class SharedProject(Project):
    objects = managers.SharedProjectManager()

    class Meta:
        proxy = True
        verbose_name = _('shared project')
        verbose_name_plural = _('shared projects')
        permissions = (
            ("list_sharedproject", "can list shared project"),
            ("detail_sharedproject", "can detail shared project"),
            ("disable_sharedproject", "can disable shared project"),
        )

    def __str__(self):
        return '{}: {} - {}'.format(self.company, self.referent, self.name)

    def clone(self, assignedCompanyId):
        """
        clone the project shared in internal projects for any company assigned to tasks
        internal tasks have to insert by hand
        """
        shared_project = Project.objects.get(pk=self.pk)
        shared_company_ids = list(self.internal_projects.all().values_list('company__id', flat=True))
        if self.tasks.count() == 0:
            raise django_exception.ProjectClonePermissionDenied(_('Please create a task before sharing a project'))
        task_list = self.tasks.filter(assigned_company_id=assignedCompanyId).exclude(
                        Q(assigned_company__in=shared_company_ids) and
                        Q(assigned_company=self.company)).order_by('assigned_company')
        for task in task_list:
            # if there are new companies
            if task.assigned_company.id not in shared_company_ids:
                shared_company_ids.append(task.assigned_company.id)
                internal_project = shared_project
                internal_project.name = task.project.name
                internal_project.company_id = task.assigned_company.id
                internal_project.referent = None
                internal_project.id = None
                internal_project.shared_project = self
                internal_project.save()


@python_2_unicode_compatible
class InternalSharedProject(Project):
    objects = managers.InternalSharedProjectManager()

    class Meta:
        proxy = True
        verbose_name = _('internal shared project')
        verbose_name_plural = _('internal shared projects')
        permissions = (
            ("list_internalsharedproject", "can list internal shared project"),
            ("detail_internalsharedproject", "can detail internal shared project"),
            ("disable_internalsharedproject", "can disable internal shared project"),
        )

    def __str__(self):
        return '{}: {} - {}'.format(self.company, self.referent, self.name)

    def clone(self, assignedCompanyId):
        """
        clone the project shared in internal projects for any company assigned to tasks
        internal tasks have to insert by hand
        """
        shared_project = Project.objects.get(pk=self.pk)
        shared_company_ids = list(self.internal_projects.all().values_list('company__id', flat=True))
        if self.tasks.count() == 0:
            raise django_exception.ProjectClonePermissionDenied(_('Please create a task before sharing a project'))
        for task in self.tasks.filter(assigned_company_id=assignedCompanyId).exclude(
                        Q(assigned_company__in=shared_company_ids) and
                        Q(assigned_company=self.company)).order_by('assigned_company'):
            # if there are new companies
            if task.assigned_company.id not in shared_company_ids:
                shared_company_ids.append(task.assigned_company.id)
                internal_project = shared_project
                internal_project.name = task.project.name
                internal_project.company_id = task.assigned_company.id
                internal_project.referent = None
                internal_project.id = None
                internal_project.shared_project = self
                internal_project.save()


@python_2_unicode_compatible
class GenericProject(Project):
    objects = managers.GenericProjectManager()

    class Meta:
        proxy = True
        verbose_name = _('generic project')
        verbose_name_plural = _('generic projects')
        permissions = (
            ("list_genericproject", "can list generic project"),
            ("detail_genericproject", "can detail generic project"),
            ("disable_genericproject", "can disable generic project"),
        )

    def __str__(self):
        return '{}: {} - {}'.format(self.company, self.referent, self.name)

    def clone(self):
        """
        clone the project shared in internal projects for any company assigned to tasks
        internal tasks have to insert by hand
        """
        shared_project = Project.objects.get(pk=self.pk)
        shared_company_ids = list(self.internal_projects.all().values_list('company__id', flat=True))
        if self.tasks.count() == 0:
            raise django_exception.ProjectClonePermissionDenied(_('Please create a task before sharing a project'))
        for task in self.tasks.exclude(
                        Q(assigned_company__in=shared_company_ids) and Q(assigned_company=self.company)).order_by(
                'assigned_company'):
            # if there are new companies
            if task.assigned_company.id not in shared_company_ids:
                shared_company_ids.append(task.assigned_company.id)
                internal_project = shared_project
                internal_project.name = task.project.name
                internal_project.company_id = task.assigned_company.id
                internal_project.referent = None
                internal_project.id = None
                internal_project.shared_project = self
                internal_project.save()

@python_2_unicode_compatible
class Post(models.Model):
    sub_task = models.ForeignKey('project.Activity', on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey('project.Task', on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey('profile.Profile', on_delete=models.CASCADE)
    is_public = models.BooleanField(
        default=True,
        verbose_name=_('is public')
    )
    text = models.TextField()
    created_date = models.DateTimeField(
            default=timezone.now)
    published_date = models.DateTimeField(
            blank=True, null=True)
    media = models.FileField(blank=True, default="", upload_to=get_upload_post_path)

    def publish(self):
        self.published_date = timezone.now()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.publish()
        super().save(force_insert=False, force_update=False, using=None,
             update_fields=None)


    def list_posts(self):
        """
        Get all company projects
        """
        return self.company.projects.filter(
            Q(profiles__in=[self.id]) | Q(company=self.company)).distinct()

    def __str__(self):
        if self.task:
            return "New post for task #" + str(self.task.id) + "by " + self.author.user.get_full_name()
        else:
            return "New post for subtask #" + str(self.sub_task.id) + "by " + self.author.user.get_full_name()

@python_2_unicode_compatible
class Comment(models.Model):
    parent = models.ForeignKey('self',
                            null=True,
                            blank=True,
                            related_name='replies',
                            on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey('profile.Profile', on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(
        default=timezone.now)

    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        permissions = (
            ("list_comment", "can list comment"),
            ("detail_comment", "can detail comment"),
            ("disable_comment", "can disable comment"),
        )
        ordering = ['-created_date']
        get_latest_by = "created_date"

    def __str__(self):
        return "Comment #" + str(self.id) + " of post #" + str(self.post.id)


@python_2_unicode_compatible
class TaskPostAssignment(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    task = models.ForeignKey('project.Task', on_delete=models.CASCADE)
    post = models.ForeignKey('project.Post', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('task')
        verbose_name_plural = _('taskpostassignments')
        permissions = (
            ("list_task_post_assignment", "can list task post assignment"),
            ("detail_task_post_assignment", "can detail task post assignment"),
            ("disable_task_post_assignment", "can disable task post assignment"),
        )
        ordering = ['-date_last_modify']
        get_latest_by = "date_create"

    def __str__(self):
        return "Post #" + str(self.post.pk) + " shared to Task #" + str(self.task.pk)


@python_2_unicode_compatible
class Task(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_('project')
    )
    name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_("name"),
    )
    assigned_company = models.ForeignKey(
        'profile.Company',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='assigned_tasks',
        verbose_name=_('assigned company'),
    )
    workers = models.ManyToManyField(
        'profile.Profile',
        through='Activity',
        related_name='tasks',
        verbose_name=_('workers')
    )
    shared_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='internal_tasks',
        verbose_name=_('shared task')
    )
    date_start = models.DateField(
        verbose_name=_('start date'),
    )
    date_end = models.DateField(
        verbose_name=_('end date'),
    )
    date_completed = models.DateField(
        blank=True, null=True,
        verbose_name=_('completed date'),
    )
    progress = models.IntegerField(
        default=0,
        verbose_name=_('progress percentage'),
    )

    class Meta:
        verbose_name = _('task')
        verbose_name_plural = _('tasks')
        permissions = (
            ("list_task", "can list task"),
            ("detail_task", "can detail task"),
            ("disable_task", "can disable task"),
        )
        ordering = ['-date_last_modify']
        get_latest_by = "date_create"

    def __str__(self):
        return '{} - {}: {} - {} ({})'.format(
            self.project.name, self.name,
            self.date_start, self.date_end,
            self.date_completed
        )

    def duration(self):
        if self.date_completed:
            days = (self.date_completed - self.date_start).days
        else:
            days = (self.date_end - self.date_start).days
        return days + 1

    def progress_with_duration(self):
        return self.progress * self.duration()

    def get_share_status(self):
        if self.project.company != self.assigned_company:
            if self.project.internal_projects.filter(company=self.assigned_company).count() == 0:
                return False
            return True
        return False

    def clone(self):
        task = Task.objects.get(pk=self.id)
        internal_project = task.project.internal_projects.filter(company=task.assigned_company).first()
        if internal_project:
            task.id = None
            task.project = internal_project
            task.assigned_company = internal_project.company
            task.shared_task = self
            task.save()
        else:
            raise django_exception.ProjectClonePermissionDenied(_('Task clone failed due to internal_project not found'))


@python_2_unicode_compatible
class Team(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name=_('project')
    )
    profile = models.ForeignKey(
        'profile.Profile',
        on_delete=models.CASCADE,
        related_name='teams',
        verbose_name=_('contact'),
    )
    role = models.CharField(
        max_length=1,
        choices=settings.PROJECT_TEAM_ROLE_CHOICES,
        verbose_name=_('role'),
    )
    project_invitation_date = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_('project invitation date'),
    )
    invitation_refuse_date = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_('invitation refuse date'),
    )

    class Meta:
        verbose_name = _('team')
        verbose_name_plural = _('teams')
        permissions = (
            ("list_team", "can list team"),
            ("detail_team", "can detail team"),
            ("disable_team", "can disable team"),
        )
        unique_together = (
            ('profile', 'project',),
        )
        ordering = ['-date_last_modify']
        get_latest_by = "date_create"

    def __str__(self):
        return '{} {} ({})'.format(
            self.project.name, self.profile, self.role,
        )

    def get_role(self):
        if self.role == settings.OWNER:
            return "Owner"
        elif self.role == settings.DELEGATE:
            return "Delegate"
        elif self.role == settings.LEVEL_1:
            return "Manager"
        elif self.role == settings.LEVEL_2:
            return "Worker"
        return self.role


@python_2_unicode_compatible
class Activity(CleanModel, UserModel, DateModel, OrderedModel):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name=_('task')
    )
    profile = models.ForeignKey(
        'profile.Profile',
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name=_('worker'),
    )
    title = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name=_("title"),
    )
    description = models.TextField(
        verbose_name=_('description'),
    )
    status = models.CharField(
        choices=settings.PROJECT_ACTIVITY_STATUS_CHOICES,
        default='to-do',
        max_length=25,
        verbose_name=_('status'),
    )
    datetime_start = models.DateTimeField(
        verbose_name=_('start date time'),
    )
    datetime_end = models.DateTimeField(
        verbose_name=_('end date time'),
    )

    class Meta:
        verbose_name = _('activity')
        verbose_name_plural = _('activities')
        permissions = (
            ("list_activity", "can list activity"),
            ("detail_activity", "can detail activity"),
            ("disable_activity", "can disable activity"),
        )
        ordering = ['-date_last_modify']
        get_latest_by = "date_create"

    def __str__(self):
        return '{} {} ({})'.format(
            self.task.name, self.profile, self.title,
        )

    @property
    def duration(self):
        return (self.datetime_end.date() - self.datetime_start.date()).days + 1
