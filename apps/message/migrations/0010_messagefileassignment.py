# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2020-09-24 23:10
from __future__ import unicode_literals

import apps.message.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0009_auto_20180203_1246'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageFileAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordering', models.IntegerField(default=0, verbose_name='ordering')),
                ('media', models.FileField(blank=True, default='', upload_to=apps.message.models.get_upload_message_file_path)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='message.Message')),
            ],
            options={
                'verbose_name': 'message file assignment',
                'verbose_name_plural': 'message filedocker assignments',
            },
        ),
    ]