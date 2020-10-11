# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-30 09:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotation', '0022_offer_start_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bom',
            options={'get_latest_by': 'date_create', 'ordering': ['-date_last_modify'], 'permissions': (('list_bom', 'can list bom'), ('detail_bom', 'can detail bom'), ('disable_bom', 'can disable bom')), 'verbose_name': 'bom', 'verbose_name_plural': 'boms'},
        ),
        migrations.AlterModelOptions(
            name='bomrow',
            options={'get_latest_by': 'date_create', 'ordering': ['-date_last_modify'], 'permissions': (('list_bomrow', 'can list bom row'), ('detail_bomrow', 'can detail bom row'), ('disable_bomrow', 'can disable bom row')), 'verbose_name': 'bom row', 'verbose_name_plural': 'bom rows'},
        ),
        migrations.AlterModelOptions(
            name='boughtoffer',
            options={'get_latest_by': 'date_create', 'ordering': ['-date_create'], 'permissions': (('list_boughtoffer', 'can list bought offer'), ('detail_boughtoffer', 'can detail bought offer')), 'verbose_name': 'ordered offer', 'verbose_name_plural': 'ordered offers'},
        ),
        migrations.AlterModelOptions(
            name='certification',
            options={'get_latest_by': 'date_create', 'ordering': ['-date_last_modify'], 'permissions': (('list_certification', 'can list certification'), ('detail_certification', 'can detail certification'), ('disable_certification', 'can disable certification')), 'verbose_name': 'certification', 'verbose_name_plural': 'certifications'},
        ),
        migrations.AlterModelOptions(
            name='favouriteoffer',
            options={'get_latest_by': 'date_create', 'ordering': ['-date_create'], 'permissions': (('list_favouriteoffer', 'can list favourite offer'), ('detail_favouriteoffer', 'can detail favourite offer')), 'verbose_name': 'favourite offer', 'verbose_name_plural': 'favourite offers'},
        ),
        migrations.AlterModelOptions(
            name='offer',
            options={'get_latest_by': 'date_create', 'ordering': ['-date_last_modify'], 'permissions': (('list_offer', 'can list offer'), ('detail_offer', 'can detail offer'), ('disable_offer', 'can disable offer')), 'verbose_name': 'offer', 'verbose_name_plural': 'offers'},
        ),
        migrations.AlterModelOptions(
            name='quotation',
            options={'get_latest_by': 'date_create', 'ordering': ['-date_last_modify'], 'permissions': (('list_quotation', 'can list quotation'), ('detail_quotation', 'can detail quotation'), ('disable_quotation', 'can disable quotation')), 'verbose_name': 'quotation', 'verbose_name_plural': 'quotations'},
        ),
        migrations.AlterModelOptions(
            name='quotationrow',
            options={'get_latest_by': 'date_create', 'ordering': ['-date_last_modify'], 'permissions': (('list_quotationrow', 'can list quotation row'), ('detail_quotationrow', 'can detail quotation row'), ('disable_quotationrow', 'can disable quotation row')), 'verbose_name': 'quotation row', 'verbose_name_plural': 'quotation rows'},
        ),
    ]
