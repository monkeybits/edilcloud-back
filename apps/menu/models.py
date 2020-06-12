# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey
from web.core.models import UserModel, DateModel, StatusModel, OrderedModel


@python_2_unicode_compatible
class Menu(MPTTModel, UserModel, DateModel, StatusModel, OrderedModel):
    name = models.CharField(
        max_length=50,
        unique=True
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('title'),
    )
    ui_sref = models.CharField(
        max_length=255,
        verbose_name=_('ui sref'),
    )
    icon = models.CharField(
        max_length=255,
        verbose_name=_('icon'),
    )
    parent = TreeForeignKey(
        'self',
        null=True, blank=True,
        related_name='children',
        db_index=True
    )

    class MPTTMeta:
        order_insertion_by = ('name',)

    class Meta:
        verbose_name = _('menu')
        verbose_name_plural = _('menus')
        permissions = (
            ("list_menu", "can list menu"),
            ("detail_menu", "can detail menu"),
            ("disable_menu", "can disable menu"),
        )

    def __str__(self):
        return "{}: {}".format(self.title, self.ui_sref)

    @classmethod
    def get_menus(cls):
        return cls.objects.filter(status=1)
