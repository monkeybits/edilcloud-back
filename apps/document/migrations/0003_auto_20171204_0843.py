# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-04 08:43
from __future__ import unicode_literals

import apps.document.models
import django.core.files.storage
from django.conf import settings
from django.db import migrations, models



class Migration(migrations.Migration):

    dependencies = [
        ('document', '0002_auto_20170713_1303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='document',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location=settings.UPLOAD_FILE_PATH), upload_to=apps.document.models.get_upload_document_path, verbose_name='certification'),
        ),
    ]
