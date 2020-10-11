# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from web.core.middleware.thread_local import get_current_user


class UserModel(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(app_label)s_%(class)s_creator",
        verbose_name=_("creator"),
    )
    last_modifier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(app_label)s_%(class)s_last_modifier',
        verbose_name=_("last modifier"),
    )

    class Meta:
        abstract = True

    def save(self, user=None, *args, **kwargs):
        user = get_current_user()
        if user:
            if self.pk:
                self.creator = user
            self.last_modifier = user
        super(UserModel, self).save(*args, **kwargs)


class DateModel(models.Model):
    date_create = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('date create'),
    )
    date_last_modify = models.DateTimeField(
        auto_now=True,
        verbose_name=_('date last modify'),
    )

    class Meta:
        abstract = True


class StatusModel(models.Model):
    STATUS_CODES = (
        (0, _('disable')),
        (1, _('enable')),
    )
    status = models.IntegerField(
        choices=STATUS_CODES,
        default=1,
        verbose_name=_('status'),
    )

    class Meta:
        abstract = True


class OrderedModel(models.Model):
    ordering = models.IntegerField(
        default=0,
        verbose_name=_('ordering'),
    )

    class Meta:
        abstract = True


class SEOModel(models.Model):
    meta_description = models.TextField(
        _("description"),
        max_length=255,
        blank=True,
    )
    meta_keywords = models.CharField(
        _("keywords"),
        max_length=255,
        blank=True,
    )
    page_title = models.CharField(
        _("title"),
        max_length=255,
        help_text=_("overwrite the title (html title tag)"),
        blank=True,
    )

    class Meta:
        abstract = True


class CleanModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.full_clean()
        super(CleanModel, self).save(*args, **kwargs)
