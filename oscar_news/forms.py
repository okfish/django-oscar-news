# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django import forms
from django.conf import settings
from taggit_autosuggest.widgets import TagAutoSuggest

from .models import News


class NewsAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NewsAdminForm, self).__init__(*args, **kwargs)
        self.fields['tags'].widget = TagAutoSuggest('taggit.Tag')

    class Meta:
        model = News
        fields = '__all__'


class LatestEntriesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(LatestEntriesForm, self).__init__(*args, **kwargs)
        self.fields['tags'].widget = TagAutoSuggest('taggit.Tag')

    class Media:
        css = {
            'all': ('%soscar_news/css/%s' % (settings.STATIC_URL, 'oscar_news_admin.css'),)
        }
