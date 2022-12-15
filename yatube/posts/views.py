from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow

POSTS_PER_PAGE = 10


def pager(request, post_list):
    return Paginator(post_list, POSTS_PER_PAGE).get_page(
        request.GET.get('page'))


@cache_page(20)
def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': pager(request, Post.objects.all()),
        'index': True
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': pager(request, group.posts.all())
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    visible = True
    if (request.user.is_authenticated
       and request.user.follower.filter(author=author)):
        following = True
    if request.user == author:
        visible = False
    return render(request, 'posts/profile.html', {
        'page_obj': pager(request, author.posts.all()),
        'author': author, 'following': following,
        'visible': visible})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': post.comments.all(),
        'form': CommentForm(request.POST or None)
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/post_create.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post,
                    files=request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.pk)
    return render(request, 'posts/post_create.html',
                  {'is_edit': True, 'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    followed_posts = Post.objects.filter(author__following__user=request.user)
    return render(request, 'posts/follow.html', {
        'page_obj': pager(request, followed_posts),
        'follow': True})


@login_required
def profile_follow(request, username):
    follower = request.user
    following = get_object_or_404(User, username=username)
    follower_list = follower.follower.all()
    print(follower_list)
    if follower != following:
        if not Follow.objects.filter(user=follower, author=following).exists():
            Follow.objects.create(user=follower, author=following)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    follower = request.user
    following = User.objects.get(username=username)
    get_object_or_404(Follow, user=follower, author=following).delete()
    return redirect('posts:profile', username=username)
