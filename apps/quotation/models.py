# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import pathlib

import datetime
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import ugettext_lazy as _

from . import managers
from web.core.models import UserModel, DateModel, StatusModel, OrderedModel, CleanModel


def get_upload_certification_path(instance, filename):
    media_dir = instance.owner.slug
    ext = pathlib.Path(filename).suffix
    filename = '{}{}'.format(slugify(instance.title), ext)
    return os.path.join(u"quotation", u"certification", media_dir, filename)


def get_upload_offer_path(instance, filename):
    media_dir = instance.owner.slug
    ext = pathlib.Path(filename).suffix
    filename = '{}{}'.format(slugify(instance.title), ext)
    return os.path.join(u"quotation", u"offers", media_dir, filename)


def get_upload_photo_path(instance, filename):
    media_dir = slugify(instance.last_name[0:2])
    ext = pathlib.Path(filename).suffix
    filename = '{}{}'.format(slugify(instance.last_name), ext)
    return os.path.join(u"offer", u"photo", u"{0}".format(media_dir), filename)


@python_2_unicode_compatible
class Bom(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    objects = managers.BomManager()
    title = models.CharField(
        max_length=255,
        verbose_name=_('title'),
    )
    description = models.TextField(
        blank=True, null=True,
        verbose_name=_('description'),
    )
    owner = models.ForeignKey(
        'profile.Company',
        on_delete=models.CASCADE,
        related_name='boms',
        verbose_name=_('owner'),
    )
    contact = models.ForeignKey(
        'profile.Profile',
        on_delete=models.CASCADE,
        related_name='material_bills',
        verbose_name=_('contact'),
    )
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='boms',
        verbose_name=_('project'),
    )
    date_bom = models.DateField(
        verbose_name=_('date'),
    )
    deadline = models.DateField(
        verbose_name=_('deadline'),
    )
    selected_companies = models.ManyToManyField(
        'profile.Company',
        blank=True,
        related_name='selected_boms',
        verbose_name=_('selected companies')
    )
    is_draft = models.BooleanField(
        default=True,
        verbose_name=_('draft')
    )
    tags = ArrayField(
        models.CharField(
            max_length=255,
            blank=True
        ),
        blank=True, null=True,
    )
    documents = GenericRelation(
        'document.Document',
        blank=True, null=True,
        related_query_name='boms'
    )
    photos = GenericRelation(
        'media.Photo',
        blank=True, null=True,
        related_query_name='boms'
    )
    videos = GenericRelation(
        'media.Video',
        blank=True, null=True,
        related_query_name='boms'
    )

    class Meta:
        verbose_name = _('bom')
        verbose_name_plural = _('boms')
        permissions = (
            ("list_bom", "can list bom"),
            ("detail_bom", "can detail bom"),
            ("disable_bom", "can disable bom"),
        )
        ordering = ['-date_last_modify']
        get_latest_by = "date_create"

    def __str__(self):
        return '{} - {}'.format(self.title, self.date_create)

    @property
    def get_tags_count(self):
        return len(self.tags) if self.tags else 0

    @property
    def get_selected_companies(self):
        return ",".join([str(company) for company in self.selected_companies.all()])

    get_selected_companies.fget.short_description = 'Selected Companies List'

    @property
    def get_selected_companies_count(self):
        return self.selected_companies.count()

    get_selected_companies_count.fget.short_description = 'Selected Companies'

    @property
    def get_bom_rows_count(self):
        return self.bom_rows.count()

    get_bom_rows_count.fget.short_description = 'Bom Rows'

    def create_bom_row(self, bom_row_dit):
        bom_row = BomRow(
            bom=self,
            **bom_row_dit
        )
        bom_row.save()
        return bom_row


@python_2_unicode_compatible
class BomRow(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    objects = managers.BomManager()
    bom = models.ForeignKey(
        'quotation.Bom',
        on_delete=models.CASCADE,
        related_name='bom_rows',
        verbose_name=_('material bill'),
    )
    typology = models.ForeignKey(
        'product.Typology',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='bom_rows',
        verbose_name=_('typology'),
    )
    category = models.ForeignKey(
        'product.Category',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='bom_rows',
        verbose_name=_('category'),
    )
    subcategory = models.ForeignKey(
        'product.Subcategory',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='bom_rows',
        verbose_name=_('subcategory'),
    )
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='bom_rows',
        verbose_name=_('product'),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('name'),
    )
    description = models.TextField(
        verbose_name=_('description'),
    )
    unit = models.ForeignKey(
        'product.Unit',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='bom_rows',
        verbose_name=_('measurement unit'),
    )
    quantity = models.DecimalField(
        blank=False, null=False,
        default=0,
        max_digits=7,
        decimal_places=2,
        verbose_name=_('quantity'),
    )

    class Meta:
        verbose_name = _('bom row')
        verbose_name_plural = _('bom rows')
        permissions = (
            ("list_bomrow", "can list bom row"),
            ("detail_bomrow", "can detail bom row"),
            ("disable_bomrow", "can disable bom row"),
        )
        ordering = ['-date_last_modify']
        get_latest_by = "date_create"

    def __str__(self):
        return u'{} {} {} {}'.format(
            self.name, self.description, self.unit, self.quantity
        )


@python_2_unicode_compatible
class Quotation(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    objects = managers.BomManager()
    title = models.CharField(
        max_length=255,
        verbose_name=_('title'),
    )
    description = models.TextField(
        blank=True, null=True,
        verbose_name=_('description'),
    )
    owner = models.ForeignKey(
        'profile.Company',
        on_delete=models.CASCADE,
        related_name='quotations',
        verbose_name=_('company'),
    )
    contact = models.ForeignKey(
        'profile.Profile',
        on_delete=models.CASCADE,
        related_name='quotations',
        verbose_name=_('contact'),
    )
    date_quotation = models.DateField(
        verbose_name=_('date'),
    )
    deadline = models.DateField(
        verbose_name=_('deadline'),
    )
    bom = models.ForeignKey(
        'quotation.Bom',
        on_delete=models.CASCADE,
        related_name='quotations',
        verbose_name=_('material bill'),
    )
    tags = ArrayField(
        models.CharField(
            max_length=255,
            blank=True
        ),
        blank=True, null=True,
    )
    is_draft = models.BooleanField(
        default=True,
        verbose_name=_('draft')
    )
    is_accepted = models.BooleanField(
        verbose_name=_('is accepted'),
        default=False,
    )
    is_completed = models.BooleanField(
        verbose_name=_('is completed'),
        default=False,
    )
    is_viewed = models.BooleanField(
        verbose_name=_('is viewed'),
        default=False,
    )
    is_confirmed = models.BooleanField(
        verbose_name=_('is confirmed'),
        default=False,
    )
    is_paid = models.BooleanField(
        verbose_name=_('is paid'),
        default=False,
    )

    class Meta:
        verbose_name = _('quotation')
        verbose_name_plural = _('quotations')
        permissions = (
            ("list_quotation", "can list quotation"),
            ("detail_quotation", "can detail quotation"),
            ("disable_quotation", "can disable quotation"),
        )
        ordering = ['-date_last_modify']
        get_latest_by = "date_create"

    def __str__(self):
        return u'{} - {}'.format(self.pk, self.date_create)

    def clean(self):
        if self.bom.is_draft:
            raise ValidationError(_('Bom still in draft'))
        if self.bom.selected_companies.count() and not self.bom.selected_companies.filter(id=self.owner.id):
            raise ValidationError(_('Owner company of  quotation is not selected from bom'))

    @property
    def get_tags_count(self):
        return len(self.tags) if self.tags else 0

    @property
    def get_quotation_rows_count(self):
        return self.quotation_rows.count()

    def get_bom_rows_id_list(self):
        return [row.bom_row_id for row in self.quotation_rows.all()]

    @property
    def is_valid_quotation(self):
        if self.deadline >= datetime.date.today():
            return True
        return False

    get_quotation_rows_count.fget.short_description = 'Quotation Rows'


@python_2_unicode_compatible
class QuotationRow(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    quotation = models.ForeignKey(
        'quotation.Quotation',
        on_delete=models.CASCADE,
        related_name='quotation_rows',
        db_index=True,
        verbose_name=_('quotation'),
    )
    bom_row = models.ForeignKey(
        'quotation.BomRow',
        on_delete=models.CASCADE,
        related_name='quotation_rows',
        verbose_name=_('material bill row'),
    )
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name=_('price'),
    )
    quantity = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name=_('quantity'),
    )
    name = models.CharField(
        blank=True, null=True,
        max_length=255,
        verbose_name=_('name'),
    )
    description = models.TextField(
        blank=True, null=True,
        verbose_name=_('description'),
    )
    note = models.TextField(
        blank=True, null=True,
        verbose_name=_('note'),
    )
    total = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=0,
        verbose_name=_('total')
    )

    class Meta:
        verbose_name = _('quotation row')
        verbose_name_plural = _('quotation rows')
        permissions = (
            ("list_quotationrow", "can list quotation row"),
            ("detail_quotationrow", "can detail quotation row"),
            ("disable_quotationrow", "can disable quotation row"),
        )
        ordering = ['-date_last_modify']
        get_latest_by = "date_create"

    def __str__(self):
        return u'{} {} {} {}'.format(
            self.name, self.description, self.price, self.quantity
        )

    def save(self, *args, **kw):
        self.total = self.get_total()
        return super(QuotationRow, self).save(*args, **kw)

    def get_total(self):
        return "%.2f" % (self.price * self.quantity)


@python_2_unicode_compatible
class Offer(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    objects = managers.OfferManager()
    owner = models.ForeignKey(
        'profile.Company',
        on_delete=models.CASCADE,
        related_name='offers',
        verbose_name=_('customer'),
    )
    contact = models.ForeignKey(
        'profile.Profile',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='offers',
        verbose_name=_('contact'),
    )
    pub_date = models.DateField(
        auto_now_add=True,
        verbose_name=_('publication date')
    )
    start_date = models.DateField(
        verbose_name=_('start date'),
    )
    deadline = models.DateField(
        verbose_name=_('deadline'),
    )
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='offers',
        verbose_name=_('product'),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('title'),
    )
    description = models.TextField(
        verbose_name=_('description'),
    )
    price = models.DecimalField(
        max_digits=9,
        decimal_places=2,

        verbose_name=_('price'),
    )
    unit = models.ForeignKey(
        'product.Unit',
        blank=True, null=True,
        related_name='offers',
        verbose_name=_('unit'),
        on_delete=models.CASCADE
    )
    tags = ArrayField(
        models.CharField(
            max_length=255,
            blank=True
        ),
        blank=True, null=True,
    )
    followers = models.ManyToManyField(
        'profile.Profile',
        through='FavouriteOffer',
        related_name='followings_offers',
        verbose_name=_('followers'),
    )
    buyers = models.ManyToManyField(
        'profile.Profile',
        through='BoughtOffer',
        related_name='buying_offers',
        verbose_name=_('buyers'),
    )
    is_draft = models.BooleanField(
        default=True,
        verbose_name=_('draft')
    )
    photo = models.ImageField(
        blank=True,
        upload_to=get_upload_offer_path,
        verbose_name=_('image'),
    )

    class Meta:
        verbose_name = _('offer')
        verbose_name_plural = _('offers')
        permissions = (
            ("list_offer", "can list offer"),
            ("detail_offer", "can detail offer"),
            ("disable_offer", "can disable offer"),
        )
        ordering = ['-date_last_modify']
        get_latest_by = "date_create"

    def __str__(self):
        return "{}: {}".format(self.owner.name, self.title)

    @property
    def get_tags_count(self):
        return len(self.tags) if self.tags else 0


@python_2_unicode_compatible
class FavouriteOffer(UserModel, DateModel):
    profile = models.ForeignKey(
        'profile.Profile',
        on_delete=models.CASCADE,
        related_name='favourite_offers',
        verbose_name=_('contact'),
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='favourite_offers',
        verbose_name=_('offer'),
    )

    class Meta:
        verbose_name = _('favourite offer')
        verbose_name_plural = _('favourite offers')
        permissions = (
            ("list_favouriteoffer", "can list favourite offer"),
            ("detail_favouriteoffer", "can detail favourite offer"),
        )
        unique_together = (('profile', 'offer',),)
        ordering = ['-date_create']
        get_latest_by = "date_create"

    def __str__(self):
        return "{} {}".format(self.profile, self.offer)


@python_2_unicode_compatible
class BoughtOffer(UserModel, DateModel):
    profile = models.ForeignKey(
        'profile.Profile',
        on_delete=models.CASCADE,
        related_name='ordered_offers',
        verbose_name=_('profile'),
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='ordered_offers',
        verbose_name=_('offer'),
    )

    class Meta:
        verbose_name = _('ordered offer')
        verbose_name_plural = _('ordered offers')
        permissions = (
            ("list_boughtoffer", "can list bought offer"),
            ("detail_boughtoffer", "can detail bought offer"),
        )
        unique_together = (('profile', 'offer',),)
        ordering = ['-date_create']
        get_latest_by = "date_create"

    def __str__(self):
        return "{} {}".format(self.profile, self.offer)


@python_2_unicode_compatible
class Certification(CleanModel, UserModel, DateModel, StatusModel, OrderedModel):
    objects = managers.CertificationManager()
    owner = models.ForeignKey(
        'profile.Company',
        on_delete=models.CASCADE,
        related_name='certifications',
        verbose_name=_('owner'),
    )
    contact = models.ForeignKey(
        'profile.Profile',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='certifications',
        verbose_name=_('contact'),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('title'),
    )
    description = models.TextField(
        verbose_name=_('description'),
    )
    document = models.FileField(
        upload_to=get_upload_certification_path,
        verbose_name=_('certification'),
    )

    class Meta:
        verbose_name = _('certification')
        verbose_name_plural = _('certifications')
        permissions = (
            ("list_certification", "can list certification"),
            ("detail_certification", "can detail certification"),
            ("disable_certification", "can disable certification"),
        )
        ordering = ['-date_last_modify']
        get_latest_by = "date_create"

    def __str__(self):
        return '{}: {}'.format(self.owner.name, self.title)


@python_2_unicode_compatible
class BomArchive(CleanModel, UserModel, DateModel):
    bom = models.ForeignKey(
        Bom,
        related_name="archived_boms",
        verbose_name=_('bom'),
        on_delete=models.CASCADE
    )
    company = models.ForeignKey(
        'profile.Company',
        related_name='archived_boms',
        verbose_name=_('company'),
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _('bom archive')
        verbose_name_plural = _('bom archives')
        permissions = (
            ("list_bomarchive", "can list bom archive"),
            ("detail_bomarchive", "can detail bom archive"),
            ("disable_bomarchive", "can disable bom archive"),
        )

    def __str__(self):
        return u'{} - {}'.format(self.bom, self.company)


@python_2_unicode_compatible
class QuotationArchive(CleanModel, UserModel, DateModel):
    quotation = models.ForeignKey(
        Quotation,
        related_name="archived_quotations",
        verbose_name=_('quotation'),
        on_delete=models.CASCADE
    )
    company = models.ForeignKey(
        'profile.Company',
        related_name='archived_quotations',
        verbose_name=_('company'),
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _('quotation archive')
        verbose_name_plural = _('quotation archives')
        permissions = (
            ("list_quotationarchive", "can list quotation archive"),
            ("detail_quotationarchive", "can detail quotation archive"),
            ("disable_quotationarchive", "can disable quotation archive"),
        )

    def __str__(self):
        return u'{} - {}'.format(self.quotation, self.company)

