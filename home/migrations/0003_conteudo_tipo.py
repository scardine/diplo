# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-29 22:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_auto_20161029_2001'),
    ]

    operations = [
        migrations.AddField(
            model_name='conteudo',
            name='tipo',
            field=models.CharField(choices=[('html', 'HTML'), ('markdown', 'Markdown')], default='html', max_length=30),
        ),
    ]
