# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os.path

from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .forms import LatestEntriesForm
from .models import NewsCategory, GenericNewsPlugin, LatestNewsPlugin, News
from .views import NEWS_LIST_TRUNCWORDS_COUNT


class NewsPlugin(CMSPluginBase):
    module = _('News')

    def get_render_template(self, context, instance, placeholder):
        return os.path.join('oscar_news', self.base_render_template)


class NewsLatestEntriesPlugin(NewsPlugin):
    """
    Non cached plugin which returns the latest posts taking into account the
      user / toolbar state
    """
    name = _('Latest News')
    model = LatestNewsPlugin
    form = LatestEntriesForm
    filter_horizontal = ('category',)
    fields = ('latest_posts', 'tags', 'category')
    cache = False
    base_render_template = 'partials/latest_entries.html'

    def render(self, context, instance, placeholder):
        context = super(NewsLatestEntriesPlugin, self).render(context, instance, placeholder)
        context['news_entries_list'] = instance.get_posts(context['request'])
        context['TRUNCWORDS_COUNT'] = NEWS_LIST_TRUNCWORDS_COUNT
        return context


class NewsTagsPlugin(NewsPlugin):
    name = _('News Tags')
    model = GenericNewsPlugin
    base_render_template = 'partials/tags.html'

    def render(self, context, instance, placeholder):
        context = super(NewsTagsPlugin, self).render(context, instance, placeholder)
        qs = News.published
        context['tags'] = qs.tag_cloud()
        return context


class NewsCategoryPlugin(NewsPlugin):
    name = _('News Categories')
    model = GenericNewsPlugin
    base_render_template = 'partials/categories.html'

    def render(self, context, instance, placeholder):
        context = super(NewsCategoryPlugin, self).render(context, instance, placeholder)
        context['categories'] = NewsCategory.get_annotated_list()
        return context

plugin_pool.register_plugin(NewsLatestEntriesPlugin)
plugin_pool.register_plugin(NewsTagsPlugin)
plugin_pool.register_plugin(NewsCategoryPlugin)
