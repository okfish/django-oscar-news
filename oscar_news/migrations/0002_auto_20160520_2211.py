# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oscar_news', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='category',
            field=models.ForeignKey(related_name='news_category', default=None, blank=True, to='oscar_news.NewsCategory', null=True, verbose_name='category'),
        ),
        migrations.AlterField(
            model_name='news',
            name='images',
            field=models.ManyToManyField(to='filer.Image', verbose_name='News images', through='oscar_news.NewsImages'),
        ),
    ]
