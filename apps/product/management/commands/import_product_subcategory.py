# coding: utf-8
"""
.. _retrieve-kpn-fax:

Bla Bla bla
=============================

Command per
utilizzo::

  dj sample

:-d: variabile Booleana per cancellare il messaggi una volta recuperati
:-l: variabile Numero per limitare il numero di messaggi recuperare
:-v: variabile Booleana per visualizzare i print
:-b, --backup: backup messages in
"""

import logging


try:
    from logutils.colorize import ColorizingStreamHandler as StreamHandler
except ImportError:
    from logging import StreamHandler

from django.core.management.base import BaseCommand

import xlrd

from apps.product.models import Category, Subcategory


class Command(BaseCommand):
    """Get all messages from configured Host
    """
    help = "Wao!"

    def add_arguments(self, parser):
        # -c enables logging using store_true
        parser.add_argument(
            '-c', '--console', action='store_true', default=False,
            help='Debug - write logging to console'
        )
        # log level
        parser.add_argument(
            '-l', '--debug-level', default='error',
            help='Set debug level (debug, info, warnings) for console',
        )
        # sheet number
        parser.add_argument(
            '-i', '--sheet_index', default=0,
            help='Set sheet_index to import',
        )

        # file name
        parser.add_argument(
            '-f', '--file', dest='filename', help='Read file in argument', default=None
        )

    output_transaction = True

    def handle(self, *args, **options):

        logger = logging.getLogger('import_generic')
        logger.setLevel(logging.INFO)

        if options.get('console'):
            console_handler = StreamHandler()
            logger.addHandler(console_handler)

        logger.info('BEGIN')

        self.import_category(options.get('filename'), options.get('sheet_index'), logger)

        logger.info('END')

    def import_category(self, filename, sheet_index, logger):

        xl_workbook = xlrd.open_workbook(filename)
        xl_sheet = xl_workbook.sheet_by_index(int(sheet_index))

        row = xl_sheet.row(0)

        if (row[0].value.lower() != 'categoria' or row[1].value.lower() != 'codice' or row[2].value.lower() != 'nome' or
            row[3].value.lower() != 'descrizione'):
            logger.info('Struttura errata del file. Le colonne corrette sono Categoria, Codice, Nome, Descrizione')
            return

        insert = 0
        error_list = list()
        for index in range(1, xl_sheet.nrows):
            try:
                row = xl_sheet.row(index)
                if row[0].ctype == 0 or row[1].ctype == 0 or row[2].ctype == 0:
                     error_list.append('riga {}: contiene valori vuoti'.format(index))
                else:
                    category = Category.objects.get(code=row[0].value)
                    obj, created = Subcategory.objects.update_or_create(
                        code=row[1].value,
                        defaults={'name': row[2].value,
                                  'description': row[3].value,
                                  'category': category,
                                  'creator_id': 1,
                                  'last_modifier_id': 1},
                    )
                    insert += 1
            except Exception as e:
                error_list.append('riga {}:{}'.format(index, e))

        logger.info('created:{}\terrors:{}'.format(
            insert,
            len(error_list)
        ))
        for error in error_list:
            logger.error(error)
        return
