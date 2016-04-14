from django.conf import settings
from django.utils.translation import override, ugettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar
from cms.toolbar.items import Break
from cms.cms_toolbars import ADMIN_MENU_IDENTIFIER, ADMINISTRATION_BREAK
from cms.utils.urlutils import admin_reverse

from .views import CURRENT_POST_IDENTIFIER

CMS_TOOLBAR_MENU_NAME = getattr(settings, 'CMS_TOOLBAR_MENU_NAME', _('Site'))


@toolbar_pool.register
class NewsToolbar(CMSToolbar):

    def get_menu_items(self, menu):
        urls = {}
        with override(self.current_lang):
            urls['news'] = admin_reverse('oscar_news_news_changelist')
            urls['add_news'] = admin_reverse('oscar_news_news_add')
            urls['categories'] = admin_reverse('oscar_news_newscategory_changelist')
            urls['add_category'] = admin_reverse('oscar_news_newscategory_add')
        menu.add_sideframe_item(_('News overview'), url=urls['news'])
        menu.add_modal_item(_('Add news'), url=urls['add_news'])
        menu.add_break('news-menu-break')
        menu.add_sideframe_item(_('News categories'), url=urls['categories'])
        menu.add_modal_item(_('Add category'), url=urls['add_category'])

    def populate(self):
        admin_menu = self.toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER, CMS_TOOLBAR_MENU_NAME)
        position = admin_menu.find_first(Break, identifier=ADMINISTRATION_BREAK)
        menu = admin_menu.get_or_create_menu('news-menu', _('News'), position=position)
        self.get_menu_items(menu)
        admin_menu.add_break('news-admin-menu-break', position=menu)
        if self.is_current_app:
            menu = self.toolbar.get_or_create_menu('oscar_news', _('News'))
            self.get_menu_items(menu)

    def add_publish_button(self):
        """
        Adds the publish button to the toolbar if the current post is unpublished
        """
        current_post = getattr(self.request, CURRENT_POST_IDENTIFIER, None)
        if (self.toolbar.edit_mode and current_post and
                not current_post.publish and
                self.request.user.has_perm('oscar_news.change_post')
            ):  # pragma: no cover  # NOQA
            classes = ['cms-btn-action', 'news-publish']
            title = _('Publish {0} now').format(current_post.title)

            url = admin_reverse('oscar_news_publish_article', args=(current_post.pk,))
            self.toolbar.add_button(title, url=url, extra_classes=classes, side=self.toolbar.RIGHT)

    def post_template_populate(self):
        current_post = getattr(self.request, CURRENT_POST_IDENTIFIER, None)
        if current_post and self.request.user.has_perm('oscar_news.change_post'):  # pragma: no cover  # NOQA
            self.add_publish_button()
