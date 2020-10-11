# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from .... import models
from web.utils import config


class BomMixin(object):
    def check_bom_owner(self, bom_id, tracking):
        """
        Check bom owner before adding bomrow
        """
        boms = models.Bom.objects.filter(
            owner=tracking.profile.company,
            id=bom_id
        )
        if not boms:
            raise PermissionDenied(config['ERROR']['BomRowAdd'])

    def check_bom_selected_companies(self, bom_id, tracking):
        """
        Check BOM selected_companies before adding quotation
        """
        bom = get_object_or_404(models.Bom.objects.filter(pk=bom_id))
        if not bom.selected_companies.filter(pk=tracking.profile.company_id).exists():
            raise PermissionDenied(config['ERROR']['QuotationAdd'])

    def get_bom(self, bom_id, tracking):
        bom = get_object_or_404(models.Bom.objects.filter(pk=bom_id))
        if bom.selected_companies.all():
            bom = get_object_or_404(bom.filter(selected_companies__in=tracking.profile.company))
        return bom

    def check_bomrow_and_quotation_owner(self, bomrow_id, quotation_id):
        """
        Check Bomrow and Quotation id, owner before adding Quotationrow
        """
        bomrows = get_object_or_404(
            models.BomRow.objects.filter(
                pk=bomrow_id,
                bom__quotations__id=quotation_id,
                bom__quotations__owner=self.tracking.profile.company,
            )
        )
        if not bomrows:
            raise PermissionDenied(config['ERROR']['QuotationRowAdd'])
