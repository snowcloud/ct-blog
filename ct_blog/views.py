from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify

from ct_blog.forms import BlogPostForm
from ct_blog.models import Post
from ct_groups.decorators import check_permission
from ct_groups.models import CTGroup
import datetime

def index(request, page=0, paginate_by=20, **kwargs):
    page_size = getattr(settings,'BLOG_PAGESIZE', paginate_by)
    
    object_list = Post.objects.public()
    return render_to_response(
        'blog/index.html',
        RequestContext( request, {'object_list': object_list }))
    
    # return list_detail.object_list(
    #     request,
    #     queryset=Post.objects.published(),
    #     paginate_by=page_size,
    #     page=page,
    #     extra={'template': 'blog/post_list.html'},
    #     **kwargs
    # )

def detail(request, object_id):
    o = get_object_or_404(Post, pk=object_id)
    # u = request.user
    # is_member = u.is_authenticated and o.has_member(u)
    # # print "is_member"
    # is_manager = is_member and o.has_manager(u)
    
    return render_to_response(
        'blog/post_detail.html',
        RequestContext( request, {'object': o }))

# def post_detail(request, slug, year, month, day, **kwargs):
#     """
#     Displays post detail. If user is superuser, view will display 
#     unpublished post detail for previewing purposes.
#     """
#     posts = None
#     if request.user.is_superuser:
#         posts = Post.objects.all()
#     else:
#         posts = Post.objects.published()
#     return date_based.object_detail(
#         request,
#         year=year,
#         month=month,
#         day=day,
#         date_field='publish',
#         slug=slug,
#         queryset=posts,
#         **kwargs
#     )
# post_detail.__doc__ = date_based.object_detail.__doc__

def _new_post(request, group):

    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.slug = slugify(post.title)[:50]
            post.publish = datetime.datetime.now()
            post.group = group
            post.save()
            return HttpResponseRedirect(post.get_absolute_url())
    else:
        form = BlogPostForm()
    return render_to_response('blog/post_add.html',
        RequestContext( request, {'form': form, 'group': group  }))

@login_required
def blog_new_post(request, group_slug):
    group = get_object_or_404(CTGroup, slug=group_slug)

    if not check_permission(request.user, group, 'blog', 'w'):
        raise PermissionDenied()

    return _new_post(request, group)

@login_required
def blog_new_site_post(request):
    if not request.user.is_staff:
        raise PermissionDenied()
    return _new_post(request, None)

def _edit_post(request, obj):

    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(obj.get_absolute_url())
    else:
        form = BlogPostForm(instance=obj)
    return render_to_response('blog/post_add.html',
        RequestContext( request, {'form': form, 'object': obj, 'group': obj.group }))

@login_required
def blog_edit_post(request, group_slug, object_id):

    obj = get_object_or_404(Post, pk=object_id)

    if not check_permission(request.user, obj.group, 'blog', 'w'):
        raise PermissionDenied()

    return _edit_post(request, obj)

@login_required
def blog_edit_site_post(request, object_id):
    if not request.user.is_staff:
        raise PermissionDenied()
    obj = get_object_or_404(Post, pk=object_id)
    return _edit_post(request, obj)


@login_required
def blog_delete_post(request, group_slug, object_id):
    obj = get_object_or_404(Post, pk=object_id)
    group = obj.group
    if not check_permission(request.user, group, 'blog', 'd'):
        raise PermissionDenied()
    ct = ContentType.objects.get_for_model(Post)    
    Comment.objects.filter(content_type=ct, object_pk=obj.id).delete()
    obj.delete()
    
    return HttpResponseRedirect(group.get_absolute_url())

def post_comment_delete(request, object_id, comment_id):
    obj = get_object_or_404(Post, pk=object_id)    
    if not check_permission(request.user, obj.group, 'comment', 'd'):
        raise PermissionDenied()
    comment = get_object_or_404(Comment, pk=comment_id)    
    comment.delete()
    return HttpResponseRedirect(obj.get_absolute_url())
    