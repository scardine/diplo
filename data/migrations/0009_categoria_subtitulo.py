# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-23 15:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0008_indicador_categoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoria',
            name='subtitulo',
            field=models.TextField(blank=True, null=True),
        ),
    ]
