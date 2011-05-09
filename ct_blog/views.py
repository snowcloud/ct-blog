from ct_blog.forms import BlogPostForm
from ct_blog.models import Post
from ct_groups.models import CTGroup



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
            post.ct_group = group
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

