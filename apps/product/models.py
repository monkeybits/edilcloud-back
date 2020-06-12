# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from apps.product import managers
from web.core.models import UserModel, DateModel, StatusModel, OrderedModel, CleanModel


@python_2_unicode_compatible
class Unit(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    objects = managers.UnitManager()
    code = models.CharField(
        max_length=255,
        verbose_name=_('code'),
        primary_key=True
    )

    class Meta:
        verbose_name = _('unit')
        verbose_name_plural = _('units')
        permissions = (
            ("list_unit", "can list unit"),
            ("detail_unit", "can detail unit"),
            ("disable_unit", "can disable unit"),
        )

    def __str__(self):
        return '{}'.format(self.code)

    @classmethod
    def get_units(cls):
        return cls.objects.filter(status=1)


@python_2_unicode_compatible
class Typology(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    objects = managers.TypologyManager()
    code = models.CharField(
        max_length=255,
        verbose_name=_('code'),
        primary_key=True
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('name')
    )
    description = models.TextField(
        blank=True, null=True,
        verbose_name=_('description'),
    )
    color = models.CharField(
        max_length=7,
        verbose_name=_('color'),
        default='#1ab394'
    )

    class Meta:
        verbose_name = _('typology')
        verbose_name_plural = _('typologies')
        permissions = (
            ("list_typology", "can list typology"),
            ("detail_typology", "can detail typology"),
            ("disable_typology", "can disable typology"),
        )

    def __str__(self):
        return '{}: {}'.format(self.code, self.name)

    def save(self, *args, **kw):
        self.name = self.name.lower()
        self.description = self.description.lower()
        super(Typology, self).save(*args, **kw)

    @property
    def complete_name(self):
        return '{} - {}'.format(self.code, self.name)


@python_2_unicode_compatible
class Category(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    objects = managers.CategoryManager()
    typology = models.ForeignKey(
        Typology,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name=_('typology'),
    )
    code = models.CharField(
        max_length=255,
        verbose_name=_('code'),
        primary_key=True
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('name')
    )
    description = models.TextField(
        blank=True, null=True,
        verbose_name=_('description'),
    )

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        permissions = (
            ("list_category", "can list category"),
            ("detail_category", "can detail category"),
            ("disable_category", "can disable category"),
        )

    def __str__(self):
        return '{}: {}'.format(self.code, self.name)

    def save(self, *args, **kw):
        self.name = self.name.lower()
        self.description = self.description.lower()
        super(Category, self).save(*args, **kw)

    @property
    def complete_name(self):
        return '{} - {}'.format(self.code, self.name)


@python_2_unicode_compatible
class Subcategory(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    objects = managers.SubcategoryManager()
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name=_('category'),
    )
    code = models.CharField(
        max_length=255,
        verbose_name=_('code'),
        primary_key=True
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('name')
    )
    description = models.TextField(
        blank=True, null=True,
        verbose_name=_('description'),
    )

    class Meta:
        verbose_name = _('subcategory')
        verbose_name_plural = _('subcategories')
        permissions = (
            ("list_subcategory", "can list subcategory"),
            ("detail_subcategory", "can detail subcategory"),
            ("disable_subcategory", "can disable subcategory"),
        )

    def __str__(self):
        return '{}: {}'.format(self.code, self.name)

    def save(self, *args, **kw):
        self.name = self.name.lower()
        self.description = self.description.lower()
        super(Subcategory, self).save(*args, **kw)

    @property
    def complete_name(self):
        return '{} - {}'.format(self.code, self.name)


@python_2_unicode_compatible
class Product(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    objects = managers.ProductManager()
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('subcategory'),
        blank=True, null=True
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='products',
        verbose_name=_('measurement unit'),
    )
    code = models.CharField(
        max_length=255,
        verbose_name=_('code'),
        primary_key=True
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('name')
    )
    description = models.TextField(
        verbose_name=_('description'),
    )
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name=_('price'),
    )

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        permissions = (
            ("list_product", "can list product"),
            ("detail_product", "can detail product"),
            ("disable_product", "can disable product"),
        )

    def __str__(self):
        return '{}: {}'.format(self.code, self.description)

    def save(self, *args, **kw):
        self.name = self.name.lower()
        self.description = self.description.lower()
        super(Product, self).save(*args, **kw)

    def get_category(self):
        return self.subcategory.category

    def get_typology(self):
        return self.get_category().typology

    @property
    def complete_name(self):
        return '{} - {}'.format(self.code, self.description)