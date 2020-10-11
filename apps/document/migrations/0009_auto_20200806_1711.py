# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2020-08-06 17:11
from __future__ import unicode_literals

import apps.document.models
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0008_auto_20200725_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='document',
            field=models.FileField(max_length=1000, storage=django.core.files.storage.FileSystemStorage(base_url='/', location='/office2017.whistle.it'), upload_to=apps.document.models.get_upload_document_path, verbose_name='certification'),
        ),
    ]
