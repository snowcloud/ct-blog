import re

from django.template import Library, Node, TemplateSyntaxError, Variable
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.db import models

Post = models.get_model('ct_blog', 'post')

register = Library()

class LatestPosts(Node):
    def __init__(self, limit, var_name):
        self.limit = int(limit)
        self.var_name = var_name

    def render(self, context):
        if context['user'].is_authenticated():
            posts = Post.objects.published()[:self.limit]
        else:
            posts = Post.objects.public()[:self.limit]
        if posts and (self.limit == 1):
            context[self.var_name] = posts[0]
        else:
            context[self.var_name] = posts
        return ''


@register.tag
def get_latest_posts(parser, token):
    """
    Gets any number of latest posts and stores them in a varable.

    Syntax::

        {% get_latest_posts [limit] as [var_name] %}

    Example usage::

        {% get_latest_posts 10 as latest_post_list %}
    """
    _syntax = u"{% get_latest_posts [limit] as [var_name] [public (optional)] %}"
    tokens = token.split_contents()
    if len(tokens) != 4:
        raise TemplateSyntaxError, "%s tag requires arguments- %s" % (token.contents.split()[0], _syntax)
    return LatestPosts(tokens[1], tokens[3])
