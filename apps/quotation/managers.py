# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q


class BomQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=1)

    def out(self, company_id):
        return self.filter(owner_id=company_id)

    def into(self, company_id):
        return self.filter(status=1).filter(Q(selected_companies__id=company_id) | Q(selected_companies__isnull=True))


class BomManager(models.Manager):
    def get_queryset(self):
        return BomQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def out(self, company_id):
        return self.get_queryset().out(company_id)

    def into(self, company_id):
        return self.get_queryset().into(company_id)


class BomRowQuerySet(models.QuerySet):
    def out(self, company_id):
        return self.filter(bom__owner_id=company_id)

    def into(self, company_id):
        return self.filter(
            bom__status=1, status=1
        ).filter(
            Q(bom__selected_companies__id=company_id) | Q(bom__selected_companies__isnull=True)
        )


class BomRowManager(models.Manager):
    def get_queryset(self):
        return BomRowQuerySet(self.model, using=self._db)

    def out(self, company_id):
        return self.get_queryset().out(company_id)

    def into(self, company_id):
        return self.get_queryset().into(company_id)


class QuotationQuerySet(models.QuerySet):
    def out(self, company_id):
        return self.filter(owner_id=company_id)

    def into(self, company_id):
        return self.filter(status=1).filter(bom__owner_id=company_id)


class QuotationManager(models.Manager):
    def get_queryset(self):
        return QuotationQuerySet(self.model, using=self._db)

    def out(self, company_id):
        return self.get_queryset().out(company_id)

    def into(self, company_id):
        return self.get_queryset().into(company_id)


class QuotationRowQuerySet(models.QuerySet):
    def out(self, company_id):
        return self.filter(quotation__owner_id=company_id)

    def into(self, company_id):
        return self.filter(
            quotation__status=1, status=1
        ).filter(
            quotation__bom__owner_id=company_id
        )


class QuotationRowManager(models.Manager):
    def get_queryset(self):
        return QuotationRowQuerySet(self.model, using=self._db)

    def out(self, company_id):
        return self.get_queryset().out(company_id)

    def into(self, company_id):
        return self.get_queryset().into(company_id)


class OfferQuerySet(models.QuerySet):
    def out(self, company_id):
        return self.filter(owner_id=company_id)


class OfferManager(models.Manager):
    def get_queryset(self):
        return OfferQuerySet(self.model, using=self._db)

    def out(self, company_id):
        return self.get_queryset().out(company_id)


class CertificationQuerySet(models.QuerySet):
    def out(self, company_id):
        return self.filter(owner_id=company_id)


class CertificationManager(models.Manager):
    def get_queryset(self):
        return CertificationQuerySet(self.model, using=self._db)

    def out(self, company_id):
        return self.get_queryset().out(company_id)
