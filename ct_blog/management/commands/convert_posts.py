from django.core.management.base import BaseCommand, CommandError

from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from ct_blog.models import Category, Post
from ct_groups.models import CTPost

class Command(BaseCommand):
    # args = '<poll_id poll_id ...>'
    help = 'Converts basic-apps blog posts to ct-blog posts'

    def handle(self, *args, **options):
        old_type = ContentType.objects.get(app_label="ct_groups", model="ctpost")
        new_type = ContentType.objects.get(app_label="ct_blog", model="post")
        print old_type, new_type
        for old_post in CTPost.objects.all():
            self.stdout.write('found "%s"\n' % old_post.title)
            new_post = Post()
            new_post.save()
            
            new_post.title = old_post.title
            new_post.slug = old_post.slug
            new_post.author = old_post.author
            new_post.body = old_post.body
            new_post.tease = old_post.tease
            new_post.status = old_post.status
            new_post.allow_comments = old_post.allow_comments
            new_post.publish = old_post.publish
            new_post.created = old_post.created
            new_post.modified = old_post.modified
            for old_c in old_post.categories.all():
                new_c, created = Category.objects.get_or_create(slug=old_c.slug, defaults={'title': old_c.title})
                new_post.categories.add(new_c)
            new_post.tags = old_post.tags
            new_post.group = old_post.group
            new_post.notified = True # stops group notification
            new_post.save()
            
            for comment in Comment.objects.filter(content_type=old_type, object_pk=old_post.id):
                comment.content_type = new_type
                comment.object_pk = new_post.id
                comment.save()
                # print comment.comment
        #     try:
        #         poll = Poll.objects.get(pk=int(poll_id))
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)
        # 
        #     poll.opened = False
        #     poll.save()
        # 
        self.stdout.write('=============\ndone it\n')