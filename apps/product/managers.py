# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models


# Todo: Add Queryset, only if chain filters are required

class TypologyManager(models.Manager):
    def active(self):
        return self.filter(
            status=1,
        )


class UnitManager(models.Manager):
    def active(self):
        return self.filter(
            status=1,
        )


class CategoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(
            typology__status=1,
            status=1,
        )

    def get_categories(self, typology_id):
        return self.filter(typology_id=typology_id)


class CategoryManager(models.Manager):
    def get_queryset(self):
        return CategoryQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def get_categories(self, typology_id):
        return self.get_queryset().get_categories(typology_id)


class SubcategoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(
            category__typology__status=1,
            category__status=1,
            status=1,
        )

    def get_sub_categories(self, category_id):
        return self.filter(category_id=category_id)


class SubcategoryManager(models.Manager):
    def get_queryset(self):
        return SubcategoryQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def get_sub_categories(self, category_id):
        return self.get_queryset().get_sub_categories(category_id)


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(
            subcategory__category__typology__status=1,
            subcategory__category__status=1,
            subcategory__status=1,
            status=1,
        )

    def get_products(self, sub_category_id):
        return self.filter(subcategory_id=sub_category_id)


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def get_products(self, sub_category_id):
        return self.get_queryset().get_products(sub_category_id)
