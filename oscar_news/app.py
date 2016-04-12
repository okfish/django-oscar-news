from django.conf.urls import url

from oscar.core.application import Application
from oscar.core.loading import get_class


class OscarNewsApplication(Application):
    name = app_name = 'oscar_news'
    detail_view = get_class('oscar_news.views', 'EntryDetailView')
    list_view = get_class('oscar_news.views', 'EntriesListView')
    category_view = get_class('oscar_news.views', 'CategoryEntriesView')
    tagged_view = get_class('oscar_news.views', 'TaggedListView')

    def get_urls(self):
        urlpatterns = super(OscarNewsApplication, self).get_urls()
        urlpatterns += [
            url(r'^$', self.list_view.as_view(), name='index'),
            url(r'^(?P<slug>\w[-\w]*)/$',
                self.detail_view.as_view(), name='entry-detail'),
            url(r'^category/(?P<category>\w[-\w]*)/$',
                self.category_view.as_view(), name='category-list'),
            url(r'^tag/(?P<tag>[-\w]+)/$',
                self.tagged_view.as_view(), name='tagged-list'),
        ]
        return self.post_process_urls(urlpatterns)

application = OscarNewsApplication()
