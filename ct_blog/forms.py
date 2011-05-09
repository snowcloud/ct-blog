from django import forms
from ct_blog.models import Post

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'body', 'tease', 'allow_comments', 'status', )
