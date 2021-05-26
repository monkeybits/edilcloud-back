# coding: utf-8

import datetime
import logging
import random
from datetime import timedelta

from faker import Factory

from django.core.management.base import BaseCommand

from apps.quotation import models as quotation_models
from apps.profile import models as profile_models
from apps.product import models as product_models

logger = logging.getLogger('file')

NUM_OWNERS = 100
NUM_COMPANIES = 10
MAX_BOMS_PER_OWNER = 100
MAX_ROWS_PER_BOM = 25
MAX_BOMROWS_PER_BOM = 5
MAX_SUPPLIERS_PER_BOM = 5
MAX_OFFERS_PER_OWNER = 100
MAX_CERTIFICATIONS_PER_OWNER = 100
MAX_BOM_SELECTED_COMPANIES = 10
tags = ['Python', 'Django', 'C++', 'Ruby', 'Java', 'Go', 'dotnet', 'Scala', 'Swift', 'Julia', 'Rust']
INTERNAL_PROJECT = 'i'


class FakeBase(object):
    model = None
    how_many = 0

    def __init__(self, opts=None):
        self.opts = opts
        self.fake = Factory.create('it-IT')

    def generate(self):
        for num in range(self.how_many):
            try:
                obj = self.model.objects.create(**self.get_map())
                logger.info('{}) {}: {}'.format(num, self.model, obj.id))
            except Exception as e:
                logger.error('{}) {}: {}'.format(num, self.model, e))

    def get_map(self):
        return {}


class FakeBom(FakeBase):
    MAX_BOM_SELECTED_COMPANIES = 50
    # return active random companies
    companies = profile_models.Company.objects.active().order_by('?')[:NUM_COMPANIES]

    def get_products(self):
        return product_models.Product.objects.active()

    def generate(self):
        owners = profile_models.OwnerProfile.objects.all()[:NUM_OWNERS]
        for owner in owners:
            for num in range(random.randint(0, MAX_BOMS_PER_OWNER)):
                current_company_id = [owner.company.id]
                all_company_ids = self.companies.values_list('id', flat=True)
                diff_company_ids = set(current_company_id).symmetric_difference(all_company_ids)
                projects = owner.company.projects.all()
                project = None
                if projects:
                    project = projects.order_by('?')[1]

                try:
                    # For testing purposes, we are initializing selected_companies variable as
                    # empty for every odd number in the iteration (num)
                    selected_companies = list()
                    if (num & 1) == 0:
                        if len(diff_company_ids) <= self.MAX_BOM_SELECTED_COMPANIES:
                            self.MAX_BOM_SELECTED_COMPANIES = len(diff_company_ids)
                        selected_companies = random.sample(
                            diff_company_ids, self.MAX_BOM_SELECTED_COMPANIES
                        )

                    # Bom dict
                    bom_dict = {
                        'title': owner.company.name + " BOM " + str(num),
                        'description': owner.company.name + " BOM Description " + str(num),
                        'date_bom': datetime.datetime.now(),
                        'deadline': datetime.datetime.now() + timedelta(days=10),
                        'project': project,
                        'tags': random.sample(tags, 2),
                        'selected_companies': selected_companies ,
                        'bom_rows': list(),
                        'is_draft': False
                    }

                    # Bom Row dict
                    bom_row_dict = list()
                    for num in range(random.randint(3, MAX_BOMROWS_PER_BOM)):
                        # Get Product information
                        product = self.get_products().order_by('?').first()
                        unit = product.unit
                        subcategory = product.subcategory
                        category = product.subcategory.category
                        typology = product.subcategory.category.typology

                        bom_row_dict.append({
                            'name': owner.company.name + " BOM ROW " + str(num),
                            'description': owner.company.name + " BOM ROW Description " + str(num),
                            'quantity': random.randint(0, 100),
                            'unit': unit,
                            'typology': typology,
                            'category': category,
                            'subcategory': subcategory,
                            'product': product
                        })

                    # Merge bom_row_dict into bom_dict
                    if bom_row_dict:
                        bom_dict['bom_rows'] = bom_row_dict

                    # Create Bom
                    bom = owner.create_bom(bom_dict)
                    logger.info('{}-{}) Owner: {} - Bom: {}'.format(
                        num, self.__class__.__name__,
                        owner.id, bom.id
                    ))
                except Exception as e:
                    logger.error('{}) Bom: {}'.format(num, e))


class FakeQuotation(FakeBase):
    MAX_BOM_SELECTED_COMPANIES = 50
    # return active random companies
    companies = profile_models.Company.objects.active().order_by('?')

    def generate(self):
        boms = quotation_models.Bom.objects.all().order_by('?')[:100]

        for num, bom in enumerate(boms):
            try:
                selected_companies = bom.selected_companies.all()
                if not selected_companies:
                    # select random companies and get rid of current bom owner (bom company)
                    suppliers = self.companies.exclude(pk=bom.owner_id)[0:MAX_SUPPLIERS_PER_BOM]
                else:
                    # only selected companies
                    suppliers = selected_companies[0:MAX_SUPPLIERS_PER_BOM]

                for supplier in suppliers:
                    # Get a random owner w.r.t. supplier company
                    owner = supplier.profiles.owners().order_by('?').first()
                    # Quotation dict
                    quotation_dict = {
                        'title': bom.title,
                        'description': bom.description,
                        'date_quotation': datetime.datetime.now().date(),
                        'deadline': datetime.datetime.now().date() + timedelta(days=10),
                        'tags': random.sample(tags, 2),
                        'bom': bom,
                        'quotation_rows': list(),
                        'is_draft': False,
                        'is_completed': True,
                    }

                    # Quotation Row dict
                    quotation_row_dict = list()
                    bom_rows = bom.bom_rows.all()
                    for bom_row in bom_rows:
                        quotation_row_dict.append({
                            'bom_row': bom_row,
                            'price': random.randint(1, 100),
                            'quantity': random.randint(1, 10),
                            'name': bom_row.name,
                            'description': bom_row.description
                        })

                    # Merge quotation_row_dict into quotation_dict
                    if quotation_row_dict:
                        quotation_dict['quotation_rows'] = quotation_row_dict

                    # Create Quotation
                    if owner:
                        quotation = owner.create_quotation(quotation_dict)
                        logger.info('{}-{}) Owner: {} - Bom: {} - Quotation: {}'.format(
                            num, self.__class__.__name__,
                            owner.id, bom.id, quotation.id
                        ))
            except Exception as e:
                logger.error('{}) Quotation: {}'.format(num, e))


class FakeOffer(object):
    def generate(self):
        owners = profile_models.OwnerProfile.objects.all()[:NUM_OWNERS]
        for owner in owners:
            for num in range(random.randint(0, MAX_OFFERS_PER_OWNER)):
                try:
                    offer = owner.create_offer({
                        'title': owner.company.name + " Offer " + str(num),
                        'description': owner.company.name + " Offer " + str(num) + " Description",
                        'price': '{}'.format(round(random.uniform(1, 100), 2)),
                        'tags': random.sample(tags, 2),
                        'pub_date': datetime.datetime.now(),
                        'deadline': datetime.datetime.now() + timedelta(days=10),
                    })
                    logger.info('{}-{}) Owner: {} - Offer: {}'.format(
                        num, self.__class__.__name__,
                        owner.id, offer.id
                    ))
                except Exception as e:
                    logger.error('{}-{}) {}'.format(
                        num, self.__class__.__name__, e
                    ))


class FakeCertification(FakeBase):
    def generate(self):
        owners = profile_models.OwnerProfile.objects.all()[:NUM_OWNERS]
        for owner in owners:
            for num in range(random.randint(0, MAX_CERTIFICATIONS_PER_OWNER)):
                try:
                    certification = owner.create_certification({
                        'title': owner.company.name + " Certification " + str(num),
                        'description': owner.company.name + " Certification " + str(num) + " Description",
                        'document': self.fake.file_name(category=None, extension=None),
                    })
                    logger.info('{}-{}) Owner: {} - Certification: {}'.format(
                        num, self.__class__.__name__,
                        owner.id, certification.id
                    ))
                except Exception as e:
                    logger.error('{}-{}) {}'.format(
                        num, self.__class__.__name__, e
                    ))


class Command(BaseCommand):
    """
    Set Products and so on
    """

    def add_arguments(self, parser):
        # -c enables logging using store_true
        parser.add_argument(
            '-c', '--console', action='store_true', default=False,
            help='Debug - write logging to console'
        )
        # -q changes opt --verbose setting to const
        parser.add_argument(
            "-q", "--quiet",
            action="store_const", const=0, dest="verbose"
        )
        # log level
        parser.add_argument(
            '-l', '--debug-level', default='error',
            help='Set debug level (debug, info, warnings) for console',
        )
        # pass data
        parser.add_argument(
            '-d', '--data', default='all',
            help=(
                'Pass data (all - All classes, bom - Bom'
                ', qtn - Quotation, o - Offer'
                ', cert - Certification)'
            )
        )

    def handle(self, *args, **options):

        level = getattr(logging, options.get('debug_level').upper())
        logger.setLevel(level)
        if options.get('console'):
            console_handler = logging._handlers['console']
            console_handler.setLevel(level)
            logger.handlers = []
            logger.addHandler(console_handler)

        # bom/all (Executes Bom)
        if options.get('data') in ['bom', 'all']:
            fake_bom = FakeBom()
            fake_bom.generate()
        # qtn/all  (Executes Quotation)
        if options.get('data') in ['qtn', 'all']:
            fake_quotation = FakeQuotation()
            fake_quotation.generate()
        # o/all  (Executes Offer)
        if options.get('data') in ['o', 'all']:
            fake_offer = FakeOffer()
            fake_offer.generate()
        # cert/all  (Executes Certification)
        if options.get('data') in ['cert', 'all']:
            fake_certification = FakeCertification()
            fake_certification.generate()
