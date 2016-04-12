# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

# import os.path

from django.conf import settings
from django.contrib.auth import get_user_model
# from django.core.exceptions import ImproperlyConfigured
# from django.core.urlresolvers import reverse
# from django.utils.timezone import now
# from django.utils.translation import get_language
from django.views.generic import DetailView, ListView

from taggit.models import Tag

from .models import NewsCategory, News

User = get_user_model()

NEWS_LIST_TRUNCWORDS_COUNT = getattr(settings, 'NEWS_LIST_TRUNCWORDS_COUNT', None)
NEWS_LIST_PAGINATION = getattr(settings, 'NEWS_LIST_PAGINATION', 5)


class BaseNewsView(object):
    model = News

    def get_queryset(self):
        queryset = self.model._default_manager.all()
        if not getattr(self.request, 'toolbar', False) or not self.request.toolbar.edit_mode:
            queryset = self.model.published.all()
        return queryset


class EntryDetailView(BaseNewsView, DetailView):

    context_object_name = 'news_entry'
    template_name = 'oscar_news/entry_detail.html'
    slug_field = 'slug'

    def get(self, *args, **kwargs):
        if hasattr(self.request, 'toolbar'):
            self.request.toolbar.set_object(self.get_object())
        return super(EntryDetailView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EntryDetailView, self).get_context_data(**kwargs)
        try:
            context['previous_entry'] = self.get_object().get_previous_by_date_published()
        except self.model.DoesNotExist:
            pass
        try:
            context['next_entry'] = self.get_object().get_next_by_date_published()
        except self.model.DoesNotExist:
            pass
        return context


class EntriesListView(BaseNewsView, ListView):

    context_object_name = 'news_entries_list'
    template_name = 'oscar_news/entries_list.html'

    def get_context_data(self, **kwargs):
        context = super(EntriesListView, self).get_context_data(**kwargs)
        context['TRUNCWORDS_COUNT'] = NEWS_LIST_TRUNCWORDS_COUNT
        return context

    def get_paginate_by(self, queryset):
        return self.paginate_by or NEWS_LIST_PAGINATION


class CategoryEntriesView(EntriesListView):

    _category = None

    @property
    def category(self):
        if not self._category:
            self._category = NewsCategory.objects.get(slug=self.kwargs['category'])
        return self._category

    def get_queryset(self):
        qs = super(CategoryEntriesView, self).get_queryset()
        if 'category' in self.kwargs:
            qs = qs.filter(category=self.category.pk)
        return qs

    def get_context_data(self, **kwargs):
        kwargs['category'] = self.category
        context = super(CategoryEntriesView, self).get_context_data(**kwargs)
        return context


class TaggedListView(EntriesListView):

    def get_queryset(self):
        qs = super(TaggedListView, self).get_queryset()
        return qs.filter(tags__slug=self.kwargs['tag'])

    def get_context_data(self, **kwargs):
        tag = Tag.objects.get(slug=self.kwargs.get('tag'))
        kwargs['tagged_entries'] = tag or None
        context = super(TaggedListView, self).get_context_data(**kwargs)
        return context
