# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-26 09:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0016_auto_20170726_0831'),
        ('project', '0003_auto_20170721_1003'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='profiles',
            field=models.ManyToManyField(related_name='projects', through='project.Team', to='profile.Profile', verbose_name='profiles'),
        ),
    ]
