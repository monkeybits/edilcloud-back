# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-03-21 14:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='typology',
            name='color',
            field=models.CharField(default='#1ab394', max_length=7, verbose_name='color'),
        ),
    ]
