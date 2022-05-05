from django.http import HttpResponse

def index(request):
    return HttpResponse('Это главная страница социальной сети Yatube')

def group_posts(request, slug):
    return HttpResponse('Это страница с постами, отфильтрованными по группам')