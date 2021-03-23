from typing import Text
from django.contrib.auth import get_user_model
from django.core import paginator
from django.core.paginator import Paginator
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django import forms
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .models import Comment, Follow, Post, Group, User
from .forms import PostForm, CommentForm


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:12]
    group_posts = group.posts.all()
    paginator = Paginator(group_posts, 12)
    group_page_number = request.GET.get('page')
    page = paginator.get_page(group_page_number)
    return render(request, 'group.html', {'group': group, 'posts': posts, 'page': page, 'paginator': paginator})

def index(request):
    post_list = Post.objects.select_related('group').order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page,
        'paginator': paginator,}
    )

def new_post(request):
    error = ''
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save()
            post.author = request.user
            form.save()
            return redirect('index')
        else:
            error = 'Пожалуйста, повторите попытку'
    form = PostForm()
    data = {
        'form': form,
        'error': error,
    }
    return render(request, 'new_post.html', data)

def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_post_list = author.posts.all()
    paginator = Paginator(author_post_list, 5)
    author_page_number = request.GET.get('page')
    auth_page = paginator.get_page(author_page_number)
    posts_count = Post.objects.filter(author=author).select_related('author').count()
    form = CommentForm(request.POST or None)
    folllowers_count = Follow.objects.filter(author__username=username).count()
    following_count = Follow.objects.filter(user__username=username).count()
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author
    ).exists()
    context = {
        'author': author,
        'page': auth_page,
        'paginator': paginator,
        'posts_count': posts_count,
        'form': form,
        'followers_count': folllowers_count,
        'following': following,
        'following_count': following_count,
    }
    return render(request, 'profile.html', context)

def post_view(request, username, post_id):
    author = User.objects.get(username=username)
    text = Post._meta.get_field('text')
    post = get_object_or_404(Post, id=post_id, author=author)
    posts_count = Post.objects.filter(author=author).select_related('author').count()
    comments = Comment.objects.filter(post=post_id).order_by('-created')
    form = CommentForm(request.POST or None)
    folllowers_count = Follow.objects.filter(author__username=username).count()
    following_count = Follow.objects.filter(user__username=username).count()
    context = {
        'text': text,
        'post': post,
        'posts_count': posts_count,
        'author': author,
        'post_id': post_id,
        'comments': comments,
        'form': form,
        'followers_count': folllowers_count,
        'following_count': following_count,
    }
    return render(request, 'post.html', context)

@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect("post", username=request.user.username, post_id=post_id)
    context = {
        'form': form,
        'post': post,
        'edited': True,
    }
    return render(
        request, 'new_post.html', context,
    ) 
 
def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )

def server_error(request):
    return render(request, "misc/500.html", status=500)

@login_required
def add_comment(request, username, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if request.GET or not form.is_valid():
        return render(request, 'post.html', {'post': post, 'form': form})
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    form.save()
    return redirect(reverse('post', kwargs={
        'username': username,
        'post_id': post_id
    }))

@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'post_list': post_list,
        'paginator': paginator,
        'page': page,
    }
    return render(request, "follow.html", context)

@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user and not Follow.objects.filter(
        user=request.user, author=author
    ).exists():
        Follow.objects.create(
            user=request.user, author=author
        )
        return redirect('profile', username=username)
    return redirect('profile', username=username)

@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)
