# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-04 15:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0018_auto_20170803_0855'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'ordering': ('ordering', 'name'), 'permissions': (('list_company', 'can list company'), ('detail_company', 'can detail company'), ('disable_company', 'can disable company')), 'verbose_name': 'company', 'verbose_name_plural': 'companies'},
        ),
        migrations.AlterModelOptions(
            name='profile',
            options={'ordering': ('ordering', 'last_name', 'first_name'), 'permissions': (('list_profile', 'can list profile'), ('detail_profile', 'can detail profile'), ('disable_profile', 'can disable profile')), 'verbose_name': 'profile', 'verbose_name_plural': 'profiles'},
        ),
        migrations.AlterUniqueTogether(
            name='partnership',
            unique_together=set([('inviting_company', 'guest_company')]),
        ),
    ]
