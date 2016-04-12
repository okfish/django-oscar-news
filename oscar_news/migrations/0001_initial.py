# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import oscar.models.fields.autoslugfield
import filer.fields.image
import taggit_autosuggest.managers
import djangocms_text_ckeditor.fields
import cms.models.fields
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cms', '0013_urlconfrevision'),
        ('taggit', '0002_auto_20150616_2121'),
        ('sites', '0001_initial'),
        ('catalogue', '0008_auto_20160130_2212'),
        ('filer', '0002_auto_20150606_2003'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenericNewsPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='LatestNewsPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('latest_posts', models.IntegerField(default=3, help_text='The number of latests articles to be displayed.', verbose_name='articles')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('meta_description', models.TextField(default=b'', verbose_name='news meta description', blank=True)),
                ('meta_keywords', models.TextField(default=b'', verbose_name='news meta keywords', blank=True)),
                ('meta_title', models.CharField(default=b'', help_text='used in title tag and social sharing', max_length=255, verbose_name='news meta title', blank=True)),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('slug', oscar.models.fields.autoslugfield.AutoSlugField(populate_from=b'title', editable=False, max_length=128, blank=True, help_text='A slug is a short name which uniquely identifies the news item', unique=True, verbose_name='Slug')),
                ('description', djangocms_text_ckeditor.fields.HTMLField(verbose_name='Description', blank=True)),
                ('publish', models.BooleanField(default=False, verbose_name='Published')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('date_published', models.DateTimeField(default=django.utils.timezone.now, verbose_name='published since')),
                ('date_published_end', models.DateTimeField(null=True, verbose_name='published until', blank=True)),
                ('enable_comments', models.BooleanField(default=False, verbose_name='enable comments on post')),
                ('author', models.ForeignKey(related_name='news_author', verbose_name='author', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-date_published',),
                'verbose_name': 'News',
                'verbose_name_plural': 'News',
            },
        ),
        migrations.CreateModel(
            name='NewsCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(unique=True, max_length=255)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(max_length=255, verbose_name='Name', db_index=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('image', models.ImageField(max_length=255, upload_to=b'categories', null=True, verbose_name='Image', blank=True)),
                ('slug', models.SlugField(max_length=255, verbose_name='Slug')),
            ],
            options={
                'ordering': ['path'],
                'verbose_name': 'News Category',
                'verbose_name_plural': 'News Categories',
            },
        ),
        migrations.CreateModel(
            name='NewsImages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', filer.fields.image.FilerImageField(related_name='news_images', blank=True, to='filer.Image', null=True)),
                ('news', models.ForeignKey(verbose_name='News', to='oscar_news.News')),
            ],
        ),
        migrations.AddField(
            model_name='news',
            name='category',
            field=models.ForeignKey(related_name='news_category', default=None, blank=True, to='oscar_news.NewsCategory', null=True),
        ),
        migrations.AddField(
            model_name='news',
            name='content',
            field=cms.models.fields.PlaceholderField(related_name='news_content', slotname=b'news_content', editable=False, to='cms.Placeholder', null=True),
        ),
        migrations.AddField(
            model_name='news',
            name='images',
            field=models.ManyToManyField(to='filer.Image', through='oscar_news.NewsImages'),
        ),
        migrations.AddField(
            model_name='news',
            name='linked_categories',
            field=models.ManyToManyField(help_text='Show news for that categories or display news on the category page', to='catalogue.Category', verbose_name="Linked product's categories", blank=True),
        ),
        migrations.AddField(
            model_name='news',
            name='linked_classes',
            field=models.ManyToManyField(help_text="Show news for that classes or display news on the specific class product's pages", to='catalogue.ProductClass', verbose_name="Linked product's classes", blank=True),
        ),
        migrations.AddField(
            model_name='news',
            name='linked_products',
            field=models.ManyToManyField(help_text="These are products that can be shown with news post or news post can be shown on the specific product's page.", to='catalogue.Product', verbose_name='Linked products', blank=True),
        ),
        migrations.AddField(
            model_name='news',
            name='sites',
            field=models.ManyToManyField(help_text='Select sites in which to show the post. If none is set it will be visible in all the configured sites.', to='sites.Site', verbose_name='Site(s)', blank=True),
        ),
        migrations.AddField(
            model_name='news',
            name='tags',
            field=taggit_autosuggest.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='latestnewsplugin',
            name='category',
            field=models.ForeignKey(default=None, to='oscar_news.NewsCategory', blank=True, help_text='Show only the blog articles tagged with chosen categories.', null=True, verbose_name='filter by category'),
        ),
        migrations.AddField(
            model_name='latestnewsplugin',
            name='tags',
            field=taggit_autosuggest.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='Show only the blog articles tagged with chosen tags.', verbose_name='filter by tag'),
        ),
    ]
