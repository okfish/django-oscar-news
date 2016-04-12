# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from .app import application

from .menu import NewsCategoriesMenu


class OscarNewsApp(CMSApp):
    """
    Allows "mounting" the oscar news and all of its urls to a specific CMS page.
    e.g at "/news/"
    """
    name = _("News for Oscar E-Commerce")
    app_name = 'oscar_news'
    urls = [
        patterns('', *application.urls[0])
    ]
    menus = [NewsCategoriesMenu]

apphook_pool.register(OscarNewsApp)
