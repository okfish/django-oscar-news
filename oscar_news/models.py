# -*- coding: utf-8 -*-
# based on original @nephila plugin https://github.com/nephila/djangocms-blog

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.utils import timezone
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.conf import settings
from django.contrib.auth import get_user_model

from cms.models import CMSPlugin, PlaceholderField

from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.image import FilerImageField
from taggit_autosuggest.managers import TaggableManager
from taggit.models import TaggedItem

from oscar.core.utils import slugify
from oscar.core.compat import AUTH_USER_MODEL
from oscar.models.fields import AutoSlugField
from oscar.apps.catalogue.abstract_models import AbstractCategory

# TODO: move defaults to the app's settings module
ENABLE_COMMENTS = getattr(settings, 'ENABLE_COMMENTS', False)
AUTHOR_DEFAULT = getattr(settings, 'AUTHOR_DEFAULT', True)
LATEST_NEWS = getattr(settings, 'LATEST_NEWS', 3)


# it's not the best place for this method but i've not found yet better way to show
# annotated tags for each instance and keep it DRY :)
def get_tag_cloud(model, queryset, tags_filter=None):
    if tags_filter is None:
        tags_filter = set()
        for item in queryset.all():
            tags_filter.update(item.tags.all())

    tags_filter = set([tag.id for tag in tags_filter])
    tags = set(TaggedItem.objects.filter(
        content_type__model=model.__name__.lower()
    ).values_list('tag_id', flat=True))

    if tags_filter is not None:
        tags = tags.intersection(tags_filter)
    tag_ids = list(tags)

    kwargs = TaggedItem.bulk_lookup_kwargs(queryset)
    kwargs['tag_id__in'] = tag_ids
    counted_tags = dict(TaggedItem.objects
                                  .filter(**kwargs)
                                  .values('tag')
                                  .annotate(count=models.Count('tag'))
                                  .values_list('tag', 'count'))
    tags = TaggedItem.tag_model().objects.filter(pk__in=counted_tags.keys())
    for tag in tags:
        tag.count = counted_tags[tag.pk]
    return sorted(tags, key=lambda x: -x.count)


class NewsManager(models.Manager):

    def tag_cloud(self):
        queryset = self.get_queryset()
        return get_tag_cloud(self.model, queryset)


class PublishedNewsManager(NewsManager):
    """
        Filters out all unpublished and items with a publication
        date in the future
    """
    def get_queryset(self):
        return super(PublishedNewsManager, self).get_queryset().filter(publish=True).\
                                                                filter(date_published__lte=timezone.now()).\
                                                                filter(Q(date_published_end__isnull=True) |
                                                                       Q(date_published_end__gte=timezone.now())
                                                                       )


class News(models.Model):
    """
    News
    """
    author = models.ForeignKey(AUTH_USER_MODEL,
                               verbose_name=_('author'), null=True, blank=True,
                               related_name='news_author')
    category = models.ForeignKey("NewsCategory", related_name="news_category",
                                 null=True, blank=True, default=None)

    meta_description = models.TextField(verbose_name=_('news meta description'),
                                        blank=True, default='')
    meta_keywords = models.TextField(verbose_name=_('news meta keywords'),
                                     blank=True, default='')
    meta_title = models.CharField(verbose_name=_('news meta title'),
                                  help_text=_('used in title tag and social sharing'),
                                  max_length=255,
                                  blank=True, default='')

    title = models.CharField(_('Title'), max_length=255)
    slug = AutoSlugField(_('Slug'), max_length=128, unique=True, editable=True,
                         populate_from='title',
                         help_text=_('A slug is a short name which uniquely'
                                     ' identifies the news item'))
    description = HTMLField(_('Description'), blank=True, configuration='CKEDITOR_SETTINGS_NEWS')
    content = PlaceholderField('news_content', related_name='news_content')

    publish = models.BooleanField(_('Published'), default=False)

    date_created = models.DateTimeField(_('created'), auto_now_add=True)
    date_modified = models.DateTimeField(_('last modified'), auto_now=True)
    date_published = models.DateTimeField(_('published since'), default=timezone.now)
    date_published_end = models.DateTimeField(_('published until'), null=True, blank=True)

    enable_comments = models.BooleanField(verbose_name=_('enable comments on post'),
                                          default=ENABLE_COMMENTS)

    images = models.ManyToManyField('filer.Image', through='NewsImages')

    # Oscar links
    linked_products = models.ManyToManyField(
                                'catalogue.Product', blank=True,
                                verbose_name=_("Linked products"),
                                help_text=_("These are products that can be shown with news post "
                                            "or news post can be shown on the specific product's page."))
    linked_categories = models.ManyToManyField(
                                'catalogue.Category', blank=True,
                                verbose_name=_("Linked product's categories"),
                                help_text=_("Show news for that categories "
                                            "or display news on the category page"))
    linked_classes = models.ManyToManyField(
                                'catalogue.ProductClass', blank=True,
                                verbose_name=_("Linked product's classes"),
                                help_text=_("Show news for that classes "
                                            "or display news on the specific class product's pages"))

    sites = models.ManyToManyField('sites.Site', verbose_name=_('Site(s)'), blank=True,
                                   help_text=_('Select sites in which to show the post. '
                                               'If none is set it will be '
                                               'visible in all the configured sites.'))

    tags = TaggableManager(blank=True, related_name='news_tags')

    objects = NewsManager()
    published = PublishedNewsManager()

    class Meta:
        app_label = 'oscar_news'
        verbose_name = _('News')
        verbose_name_plural = _('News')
        ordering = ('-date_published', )

    def __unicode__(self):
        return self.title

    @property
    def is_published(self):
        """
        Checks whether the news entry is *really* published by checking publishing dates too
        """
        return (self.publish and
                (self.date_published and self.date_published <= timezone.now()) and
                (self.date_published_end is None or self.date_published_end > timezone.now())
                )

    def _set_default_author(self, current_user):
        if not self.author_id:
            if AUTHOR_DEFAULT is True:
                user = current_user
            else:
                user = get_user_model().objects.get(username=AUTHOR_DEFAULT)
            self.author = user

    def get_absolute_url(self):
        """
        method below inherited and slightly customized
        """
        cache_key = 'NEWS_ENTRY_URL_%s' % self.pk
        url = cache.get(cache_key)
        if not url:
            # temporarily use link to news detail
            url = reverse(
                'oscar_news:entry-detail',
                kwargs={'slug': self.slug})
            cache.set(cache_key, url)
        return url

    def get_tags(self, queryset=None):
        """
        :return: the list of object's tags annotated with counters.
        Tags are limited by published news.
        """
        queryset = queryset or News.published.get_queryset()
        return get_tag_cloud(self.__class__, queryset, set(self.tags.all()))

    def get_all_tags(self):
        """
        :return: List of all object's tags including unpublished
        """
        return self.get_tags(News.objects.all())


class NewsCategory(AbstractCategory):

    def get_absolute_url(self):
        """
        method below inherited and slightly customized
        """
        cache_key = 'NEWS_CATEGORY_URL_%s' % self.pk
        url = cache.get(cache_key)
        if not url:
            # temporarily use link to category list
            url = reverse(
                'oscar_news:category-list',
                kwargs={'category': self.slug})
            cache.set(cache_key, url)
        return url

    # it's the hack from http://stackoverflow.com/a/6379556
    # so, if further django's version will provide a field inheritance
    # in proper way this constructor can be removed
    def __init__(self, *args, **kwargs):
        super(NewsCategory, self).__init__(*args, **kwargs)
        self._meta.get_field('image').upload_to = 'news/categories'

    class Meta:
        app_label = 'oscar_news'
        ordering = ['path']
        verbose_name = _('News Category')
        verbose_name_plural = _('News Categories')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(NewsCategory, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.full_name


class NewsImages(models.Model):
    news = models.ForeignKey('News', verbose_name=_("News"))
    image = FilerImageField(null=True, blank=True,
                            related_name="news_images")


class BaseNewsPlugin(CMSPlugin):
    app_name = 'oscar_news'

    class Meta:
        abstract = True

    def post_queryset(self, request=None):
        entries = News._default_manager
        if not request or not getattr(request, 'toolbar', False) or not request.toolbar.edit_mode:
            entries = News.published
        return entries.all()


@python_2_unicode_compatible
class LatestNewsPlugin(BaseNewsPlugin):
    latest_posts = models.IntegerField(_('articles'), default=LATEST_NEWS,
                                       help_text=_(u'The number of latests '
                                                   u'articles to be displayed.'))
    tags = TaggableManager(_('filter by tag'), blank=True,
                           help_text=_('Show only the blog articles tagged with chosen tags.'),
                           related_name='oscar_news_latest_entry')

    category = models.ForeignKey("oscar_news.NewsCategory",
                                 verbose_name=_('filter by category'),
                                 help_text=_('Show only the blog articles tagged '
                                             u'with chosen categories.'),
                                 null=True, blank=True, default=None)

    def __str__(self):
        return force_text(_('%s latest articles by tag') % self.latest_posts)

    def copy_relations(self, oldinstance):
        for tag in oldinstance.tags.all():
            self.tags.add(tag)
        self.category = oldinstance.category

    def get_posts(self, request):
        posts = self.post_queryset(request)
        if self.tags.exists():
            posts = posts.filter(tags__in=list(self.tags.all()))
        if self.category is not None:
            posts = posts.filter(category=self.category)
        return posts.distinct()[:self.latest_posts]


@python_2_unicode_compatible
class GenericNewsPlugin(BaseNewsPlugin):

    class Meta:
        abstract = False

    def __str__(self):
        return force_text(_('generic news plugin'))
