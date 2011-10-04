from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Manager, permalink, Q
from django.contrib.auth.models import User
from django.conf import settings
from django.template.defaultfilters import truncatewords_html
from django.template.loader import render_to_string

import datetime
import tagging
from tagging.fields import TagField

from ct_groups.models import CTGroup, group_notify


class Category(models.Model):
    """Category model."""
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ('title',)

    def __unicode__(self):
        return u'%s' % self.title

    @permalink
    def get_absolute_url(self):
        return ('blog_category_detail', None, {'slug': self.slug})

class PublicManager(Manager):
    """Returns published posts that are not in the future."""
    
    def published(self):
        return self.get_query_set().filter(status__gte=2, publish__lte=datetime.datetime.now())

    def public(self):
        return self.published().filter(Q(group__isnull=True) | (Q(group__is_public=True) & 
            Q(group__ctgrouppermission__name__exact='blog', group__ctgrouppermission__read_permission__exact='10')))

class Post(models.Model):
    """Post model."""
    STATUS_CHOICES = (
        (1, _('Draft')),
        (2, _('Public')),
    )
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), unique_for_date='publish')
    author = models.ForeignKey(User, blank=True, null=True, related_name="post_author")
    body = models.TextField(_('body'), )
    tease = models.TextField(_('tease'), blank=True, help_text=_('Concise text suggested. Does not appear in RSS feed.'))
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=2)
    allow_comments = models.BooleanField(_('allow comments'), default=True)
    publish = models.DateTimeField(_('publish'), default=datetime.datetime.now)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    categories = models.ManyToManyField(Category, blank=True)
    tags = TagField()
    group = models.ForeignKey(CTGroup, blank=True, null=True)
    notified = models.BooleanField(default=False)
    objects = PublicManager()

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')
        ordering  = ('-publish',)
        get_latest_by = 'publish'

    def __unicode__(self):
        return u'%s' % self.title

    @permalink
    def get_absolute_url(self):
        return ('post', None, {
            'object_id': self.id,
            # 'month': self.publish.strftime('%b').lower(),
            # 'day': self.publish.day,
            # 'slug': self.slug
        })

    def get_previous_post(self):
        return self.get_previous_by_publish(status__gte=2)

    def get_next_post(self):
        return self.get_next_by_publish(status__gte=2)

    def save(self, *args, **kwargs):
        super(Post, self).save(*args, **kwargs)
        if not self.notified:
            if self.status > 1 and self.publish and self.publish <= datetime.datetime.now():
                if self.group:
                    group_notify(self)
                self.notified = True
                super(Post, self).save(*args, **kwargs)

    def _summary(self):    
        if self.tease:
            return self.tease
        else:
            return truncatewords_html(self.body, 80)
            
    summary = property(_summary)
    
    def get_notify_content(self, comment=None):
        """docstring for get_notify_content"""
        from django.contrib.comments.models import Comment
        
        if comment:
            if not isinstance(comment, Comment):
                comment = Comment.objects.get(pk=comment)
            line_1 = _("A comment has been added to: %s.") % self.title
            author= comment.user.get_full_name()
            content = comment.comment
            url = '%s%s#comment' % ( settings.APP_BASE[:-1], self.get_absolute_url())           
        else:
            line_1 = _('A discussion post has been added to: %s.') % self.group.name
            author= self.author.get_full_name()
            content = '%s\n%s' % (self.title, self.summary)
            url = '%s%s' % ( settings.APP_BASE[:-1], self.get_absolute_url())
                    
        content = render_to_string('ct_groups/email_post_comment_content.txt', {
            'line_1': line_1,
            'line_2': '',
            'author': author, 
            'review_date': self.publish.strftime("%d/%m/%Y, %H.%M"),
            'content': content,
            'url': url
        })    
        return (True, content)


# class BlogRoll(models.Model):
#     """Other blogs you follow."""
#     name = models.CharField(max_length=100)
#     url = models.URLField(verify_exists=False)
#     sort_order = models.PositiveIntegerField(default=0)
# 
#     class Meta:
#         ordering = ('sort_order', 'name',)
#         verbose_name = _('blog roll')
#         verbose_name_plural = _('blog roll')
# 
#     def __unicode__(self):
#         return self.name
# 
#     def get_absolute_url(self):
#         return self.url