# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.db.models import Q


class ProjectQuerySet(models.QuerySet):
    def active(self):
        return self.filter(
            status=1
        )

    def internal_projects(self):
        # Todo
        return self.all()

    def shared_projects(self):
        # Todo
        return self.all()

    def internal_shared_projects(self):
        # Todo
        return self.all()

    def generic_projects(self):
        # Todo
        return self.all()


class ProjectManager(models.Manager):
    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def internal_projects(self):
        return self.get_queryset().internal_projects()

    def shared_projects(self):
        return self.get_queryset().shared_projects()

    def internal_shared_projects(self):
        return self.get_queryset().internal_shared_projects()

    def generic_projects(self):
        return self.get_queryset().generic_projects()


class InternalProjectManager(ProjectManager):
    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self._db).active().internal_projects()


class SharedProjectManager(ProjectManager):
    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self._db).shared_projects()


class InternalSharedProjectManager(ProjectManager):
    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self._db).internal_shared_projects()


class GenericProjectManager(ProjectManager):
    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self._db).generic_projects()
