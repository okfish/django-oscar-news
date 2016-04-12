from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OscarNewsConfig(AppConfig):
    label = 'oscar_news'
    name = 'oscar_news'
    verbose_name = _('Simple News app for Oscar and Django-CMS')

