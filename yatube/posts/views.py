from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from posts.forms import CommentForm, PostForm
from posts.models import Comment, Follow, Group, Post

from yatube.settings import POSTS_PER_PAGE

User = get_user_model()


def index(request):
    template = 'posts/index.html'
    page_title = 'Последние обновления на сайте'

    posts = Post.objects.select_related('group', 'author').all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': page_title,
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(
        Comment.objects.select_related('post'),
        id=comment_id
    )
    if comment.author != request.user:
        return redirect('posts:post_detail', post_id=comment.post.id)
    comment.delete()
    return redirect('posts:post_detail', post_id=comment.post.id)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    page_title = 'Новый пост'

    if request.method != 'POST':
        form = PostForm()
        context = {
            'page_title': page_title,
            'form': form
        }
        return render(request, template, context)

    form = PostForm(request.POST, files=request.FILES or None)
    if not form.is_valid():
        context = {
            'page_title': page_title,
            'form': form
        }
        return render(request, template, context)
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('posts:profile', username=request.user.username)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    page_title = 'Последние обновления у избранных авторов'

    posts = (Post.objects.select_related('group', 'author').
             filter(author__following__user=request.user))
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': page_title,
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    page_title = f'Записи сообщества {group.title}'

    posts = group.posts.select_related('author').all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': page_title,
        'page_obj': page_obj,
        'group': group
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    page_title = f'Профайл пользователя @{author.username}'
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user.id,
            author=author,
        ).exists()
    else:
        following = False

    posts = author.posts.select_related('group').all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': page_title,
        'page_obj': page_obj,
        'author': author,
        'following': following,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    subscription = Follow.objects.filter(
        user=request.user,
        author=author
    )
    if subscription.exists():
        subscription.delete()
    return redirect('posts:profile', username=username)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(
        Post.objects.select_related('group', 'author'),
        id=post_id
    )
    comments = post.comments.select_related('author').all()
    page_title = f'Пост {str(post)}'
    form = CommentForm()

    context = {
        'page_title': page_title,
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, template, context)


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
def post_delete(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author'),
        id=post_id
    )
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    post.delete()
    return redirect('posts:profile', username=post.author.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)

    template = 'posts/create_post.html'
    page_title = 'Редактировать пост'

    if request.method != 'POST':
        form = PostForm(instance=post)
        context = {
            'page_title': page_title,
            'form': form
        }
        return render(request, template, context)

    form = PostForm(request.POST, files=request.FILES or None, instance=post)
    if not form.is_valid:
        context = {
            'page_title': page_title,
            'form': form
        }
        return render(request, template, context)
    form.save()
    return redirect('posts:post_detail', post_id=post_id)
