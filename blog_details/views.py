from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count

# Create your views here.


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 2
    template_name = 'blog_details/post/list.html'

def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 2)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)
    print(posts)
    return render(request, 'blog_details/post/list.html',{'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED, publish__year=year, publish__month=month, publish__day=day, slug=post)
    comments = post.comments.filter(active=True)
    form = CommentForm()
    post_tags = post.tags.all()
    print(post_tags)
    similar_posts = Post.published.filter(tags__in=post_tags).exclude(id=post.id) #get all post that has these tags included
    similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
    similar_posts = list(set(similar_posts))
    return render(request,'blog_details/post/detail.html', {'post': post, 'comments': comments, 'form': form, 'similar_posts': similar_posts})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends {post.title}"
            message = f" Read {post.title} at {post_url} \n\n {cd['name']}'s comment: {cd['comments']}"
            send_mail(subject=subject, message=message, from_email="jeffmaine221@gmail.com", recipient_list=[cd["to"]], fail_silently=False)
            sent = True
            return render(request, 'blog_details/post/share.html', {'sent': sent,'post': post})
        else:
            return render(request, 'blog_details/post/share.html', {"form": form})
    else:
        form = EmailPostForm()
    return render(request, 'blog_details/post/share.html', {"form": form})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED, id=post_id)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blog_details/post/comment.html', {"form": form, 'post': post, 'comment': comment})
