# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

# from copy import deepcopy

from cms.admin.placeholderadmin import FrontendEditableAdminMixin, PlaceholderAdminMixin
# from django import forms
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
# from django.utils.six import callable
from django.utils.translation import get_language_from_request, ugettext_lazy as _
from django.contrib.admin import ModelAdmin, TabularInline

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .forms import NewsAdminForm
from .models import NewsCategory, News, NewsImages

try:
    from admin_enhancer.admin import EnhancedModelAdminMixin
except ImportError:
    class EnhancedModelAdminMixin(object):
        pass


class ImagesInlineAdmin(TabularInline):
    model = News.images.through
    extra = 5


class NewsCategoryAdmin(EnhancedModelAdminMixin, TreeAdmin):
    form = movenodeform_factory(NewsCategory)
    prepopulated_fields = {"slug": ("name",)}
    class Media:
        css = {
            'all': ('%soscar_news/css/%s' % (settings.STATIC_URL, 'oscar_news_admin.css'),)
        }

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}


class NewsAdmin(FrontendEditableAdminMixin, PlaceholderAdminMixin,  ModelAdmin):
    form = NewsAdminForm
    list_display = [
        'title', 'author', 'date_published',
        'date_published_end'
    ]
    list_filter = ('sites',)
    date_hierarchy = 'date_published'
    raw_id_fields = ['author']
    frontend_editable_fields = ('title', 'description', 'content')

    enhance_exclude = ('images',)
    fieldsets = [
        (None, {
            'fields': [('title', 'category', 'publish', ),
                       ('description', )
                       ]
        }),
        ('Info', {
            'fields': [('slug', 'tags'),
                       ('date_published', 'date_published_end', ),
                       ('enable_comments',)],
            'classes': ('collapse',)
        }),
         # ('Images', {
         #     'fields': (('images',),),
         #     'classes': ('collapse',)
         # }),
        ('SEO', {
            'fields': [('meta_description', 'meta_title', 'meta_keywords')],
            'classes': ('collapse',)
        }),
        ('E-Commerce', {
            'fields': [('linked_classes', 'linked_categories', 'linked_products')],
            'classes': ('collapse',)
        }),
    ]
    prepopulated_fields = {"slug": ("title",)}

    inlines = (ImagesInlineAdmin,)

    def get_urls(self):
        """
        Customize the modeladmin urls
        """
        urls = [
            url(r'^publish/([0-9]+)/$', self.admin_site.admin_view(self.publish_post),
                name='oscar_news_publish_article'),
        ]
        urls.extend(super(NewsAdmin, self).get_urls())
        return urls

    def publish_post(self, request, pk):
        """
        Admin view to publish a single post
        :param request: request
        :param pk: primary key of the post to publish
        :return: Redirect to the post itself (if found) or fallback urls
        """
        language = get_language_from_request(request, check_path=True)
        try:
            post = News.objects.get(pk=int(pk))
            post.publish = True
            post.save()
            return HttpResponseRedirect(post.get_absolute_url(language))
        except Exception:
            try:
                return HttpResponseRedirect(request.META['HTTP_REFERER'])
            except KeyError:
                return HttpResponseRedirect(reverse('oscar_news:posts-latest'))

    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     field = super(PostAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    #     if db_field.name == 'meta_description':
    #         original_attrs = field.widget.attrs
    #         original_attrs['maxlength'] = 160
    #         field.widget = forms.TextInput(original_attrs)
    #     elif db_field.name == 'meta_title':
    #         field.max_length = 70
    #     return field

    # def get_fieldsets(self, request, obj=None):
    #     """
    #     Customize the fieldsets according to the app settings
    #     :param request: request
    #     :param obj: post
    #     :return: fieldsets configuration
    #     """
    #     app_config_default = self._app_config_select(request, obj)
    #     if app_config_default is None and request.method == 'GET':
    #         return super(PostAdmin, self).get_fieldsets(request, obj)
    #     if not obj:
    #         config = app_config_default
    #     else:
    #         config = obj.app_config
    #
    #     fsets = deepcopy(self._fieldsets)
    #     if config:
    #         if config.use_abstract:
    #             fsets[0][1]['fields'].append('abstract')
    #         if not config.use_placeholder:
    #             fsets[0][1]['fields'].append('post_text')
    #     else:
    #         if get_setting('USE_ABSTRACT'):
    #             fsets[0][1]['fields'].append('abstract')
    #         if not get_setting('USE_PLACEHOLDER'):
    #             fsets[0][1]['fields'].append('post_text')
    #     if get_setting('MULTISITE'):
    #         fsets[1][1]['fields'][0].append('sites')
    #     if request.user.is_superuser:
    #         fsets[1][1]['fields'][0].append('author')
    #     filter_function = get_setting('ADMIN_POST_FIELDSET_FILTER')
    #     if callable(filter_function):
    #         fsets = filter_function(fsets, request, obj=obj)
    #     return fsets

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        obj._set_default_author(request.user)
        super(NewsAdmin, self).save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('%soscar_news/css/%s' % (settings.STATIC_URL, 'oscar_news_admin.css'),)
        }


admin.site.register(NewsCategory, NewsCategoryAdmin)

admin.site.register(News, NewsAdmin)
