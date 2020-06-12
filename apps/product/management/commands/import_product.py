# coding: utf-8
"""
Command to import Units, Typologies, Categories, Subcategories and Products
"""

import os
import logging

from xml.dom import minidom

from django.core.management.base import BaseCommand

from ... import models
from django.conf import settings

logger = logging.getLogger('file')
measurement_unit_dict = dict()


# UTILS METHODS
def get_attributes_node(node):
    attr_dict = dict()
    attributes = node.attributes.items()
    for attr in attributes:
        attr_dict[attr[0]] = attr[1]
    return attr_dict


def get_attr_dict(node):
    attr_dict = get_attributes_node(node)
    child_descr = node.getElementsByTagName('prdDescrizione')[0]
    attr_dict.update(get_attributes_node(child_descr))
    child_quot = node.getElementsByTagName('prdQuotazione')[0]
    attr_dict.update(get_attributes_node(child_quot))
    return attr_dict


# GET_OR_CREATE METHODS
def get_or_create_typology(typ_code, cat_code):
    typology_dict = dict(settings.PRODUCT_TYPOLOGY_NAMES)
    if typ_code in typology_dict:
        description = typology_dict[typ_code]
    else:
        description = typ_code
    typology, t_created = models.Typology.objects.get_or_create(
        code=typ_code, defaults={
            'creator_id': 1, 'last_modifier_id': 1,
            'name': description, 'description': description
        }
    )
    full_code = '{0}.{1}'.format(typ_code, cat_code)
    return typology, full_code


def get_or_create_category(typ_code, cat_code, sub_code, full_code, typology):
    category, c_created = models.Category.objects.get_or_create(
        code=full_code, defaults={
            'creator_id': 1, 'last_modifier_id': 1,
            'name': full_code, 'description': full_code, 'typology': typology
        }
    )
    full_code = '{0}.{1}.{2}'.format(typ_code, cat_code, sub_code)
    return category, full_code


def get_or_create_subcategory(full_code, category):
    subcategory, s_created = models.Subcategory.objects.get_or_create(
        code=full_code, defaults={
            'creator_id': 1, 'last_modifier_id': 1,
            'name': full_code, 'description': full_code, 'category': category
        }
    )
    return subcategory


def get_or_create_product(attr_dict, subcategory):
    try:
        mu_code = measurement_unit_dict[attr_dict['unitaDiMisuraId']]
        measurement_unit = models.Unit.objects.get(code=mu_code)
    except KeyError:
        logger.info("prodotto senza unità di misura!")
        measurement_unit = None

    product, created = models.Product.objects.get_or_create(
        code=attr_dict['prdId'], defaults={
            'creator_id': 1, 'last_modifier_id': 1,
            'name': attr_dict['breve'],
            'description': attr_dict['estesa'],
            'price': attr_dict['valore'],
            'unit': measurement_unit,
            'subcategory': subcategory,
        }
    )
    return created, product


# COMMAND METHODS
def product_creation(parsed):
    for node in parsed.getElementsByTagName('prodotto'):
        attr_dict = get_attr_dict(node)
        product_id = attr_dict['prdId']
        point_counter = product_id.count('.')
        if point_counter == 4:
            if not product_id.endswith('.Z'):
                typ_code, cat_code, sub_code = attr_dict['prdId'].split('.')[0:3]
                if ',' in cat_code:
                    logger.info("ERROR: {}: contains comma (,)".format(cat_code))
                else:
                    typology, full_code = get_or_create_typology(typ_code, cat_code)
                    category, full_code = get_or_create_category(typ_code, cat_code, sub_code, full_code, typology)
                    subcategory = get_or_create_subcategory(full_code, category)
                    created, product = get_or_create_product(attr_dict, subcategory)
                    logger.info("{}: {}".format(created, product))

    for node in parsed.getElementsByTagName('prodotto'):
        attr_dict = get_attr_dict(node)
        product_id = attr_dict['prdId']
        point_counter = product_id.count('.')

        if point_counter == 3:
            product_exist = bool(models.Product.objects.filter(code__startswith=product_id).count())
            if not product_exist:
                typ_code, cat_code, sub_code = attr_dict['prdId'].split('.')[0:3]
                if ',' in cat_code:
                    logger.info("ERROR: {}: contains comma (,)".format(cat_code))
                else:
                    typology, full_code = get_or_create_typology(typ_code, cat_code)
                    category, full_code = get_or_create_category(typ_code, cat_code, sub_code, full_code, typology)
                    subcategory = get_or_create_subcategory(full_code, category)
                    created, product = get_or_create_product(attr_dict, subcategory)
                    logger.info("{}: {}".format(created, product))


def product_update_description(parsed):
    for node in parsed.getElementsByTagName('prodotto'):
        attr_dict = get_attr_dict(node)
        product_id = attr_dict['prdId']
        point_counter = product_id.count('.')
        if point_counter == 3 and (models.Product.objects.filter(code__startswith=attr_dict['prdId']).count() > 1):
            description = attr_dict['estesa']
            for product_son in models.Product.objects.filter(code__startswith=attr_dict['prdId']):
                if description.lower() not in product_son.description:
                    product_son.description = u'{0} {1}'.format(description, product_son.description)
                    product_son.save()
                    logger.info(product_son.code)


def category_update(parsed):
    for node in parsed.getElementsByTagName('prodotto'):
        attr_dict = get_attributes_node(node)
        if len(attr_dict['prdId'].split('.')) == 2:
            child_descr = node.getElementsByTagName('prdDescrizione')[0]
            attr_dict.update(get_attributes_node(child_descr))

            typ_code, cat_code = attr_dict['prdId'].split('.')[0:2]
            if ',' in cat_code:
                logger.info("ERROR: {}: contains comma (,)".format(cat_code))
            else:
                cat_code = '{0}.{1}'.format(typ_code, cat_code)
                try:
                    category, created = models.Category.objects.update_or_create(
                        code=cat_code, defaults={
                            'creator_id': 1, 'last_modifier_id': 1,
                            'name': attr_dict['breve'],
                            'description': attr_dict['estesa'],
                        }
                    )
                    logger.info("{}: {}".format(created, category))
                except Exception as e:
                    logger.info("{}: {}".format(attr_dict, e))


def subcategory_update(parsed):
    for node in parsed.getElementsByTagName('prodotto'):
        attr_dict = get_attributes_node(node)
        if len(attr_dict['prdId'].split('.')) == 3:
            child_descr = node.getElementsByTagName('prdDescrizione')[0]
            attr_dict.update(get_attributes_node(child_descr))

            typ_code, cat_code, sub_code = attr_dict['prdId'].split('.')[0:3]
            if ',' in cat_code:
                logger.info("ERROR: {}: contains comma (,)".format(cat_code))
            else:
                sub_code = '{0}.{1}.{2}'.format(typ_code, cat_code, sub_code)
                try:
                    subcategory, created = models.Subcategory.objects.update_or_create(
                        code=sub_code, defaults={
                            'creator_id': 1, 'last_modifier_id': 1,
                            'name': attr_dict['breve'],
                            'description': attr_dict['estesa'],
                        }
                    )
                    logger.info("{}: {}".format(created, subcategory))
                except Exception as e:
                    logger.info("{}: {}".format(attr_dict, e))


def unit_update(parsed):
    for node in parsed.getElementsByTagName('unitaDiMisura'):
        attr_dict = get_attributes_node(node)
        measurement_unit_dict[attr_dict['unitaDiMisuraId']] = attr_dict['udmId']
        m_unit, created = models.Unit.objects.get_or_create(
            code=attr_dict['udmId'], defaults={'creator_id': 1, 'last_modifier_id': 1}
        )
        logger.info("{}: {}".format(created, m_unit))


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
        # file path
        parser.add_argument(
            '-f', '--file', dest='filename', default=None,
            help='Read file in argument'
        )

    output_transaction = True

    def get_file_path(self):
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'prezzario_m215.xml'
        )

    def check_file_path(self):
        if not os.path.isfile(self.filename):
            raise FileNotFoundError

    def check_file_extension(self):
        if '.xml' not in os.path.splitext(self.filename):
            raise Exception('FILE IS INVALID')

    def handle(self, *args, **options):
        level = getattr(logging, options.get('debug_level').upper())
        logger.setLevel(level)
        if options.get('console'):
            console_handler = logging._handlers['console']
            console_handler.setLevel(level)
            logger.handlers = []
            logger.addHandler(console_handler)

        self.filename = options.get('filename')
        if not self.filename:
            self.filename = self.get_file_path()

        self.check_file_path()
        self.check_file_extension()
        with open(self.filename, 'r') as file_xml:
            doc = file_xml
            parsed = minidom.parse(doc)
            unit_update(parsed)
            product_creation(parsed)
            category_update(parsed)
            subcategory_update(parsed)
            product_update_description(parsed)
