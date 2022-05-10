from django.shortcuts import get_object_or_404, render
from posts.models import Group, Post


def index(request):
    template = 'posts/index.html'
    text = 'Последние обновления на сайте'
    posts = Post.objects.all()[:10]
    context = {
        'text': text,
        'posts': posts
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    text = f'Записи сообщества {group.title}'
    posts = group.posts.all()[:10]
    context = {
        'text': text,
        'group': group,
        'posts': posts
    }
    return render(request, template, context)
