from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify

from ct_blog.forms import BlogPostForm
from ct_blog.models import Post
from ct_groups.models import CTGroup
import datetime

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


@login_required
def blog_new_post(request, group_slug):
    group = get_object_or_404(CTGroup, slug=group_slug)

    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.slug = slugify(post.title)
            post.publish = datetime.datetime.now()
            post.group = group
            print post.id, group
            post.save()
            return HttpResponseRedirect(post.get_absolute_url())
    else:
        form = BlogPostForm()
    return render_to_response('blog/post_add.html',
        RequestContext( request, {'form': form,  }))


@login_required
def blog_post_edit(request, group_slug, slug):

    obj = get_object_or_404(Post, slug=slug)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(obj.get_absolute_url())
    else:
        form = BlogPostForm(instance=obj)
    return render_to_response('blog/post_add.html',
        RequestContext( request, {'form': form, 'object': obj }))

