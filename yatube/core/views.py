from django.shortcuts import render


def csrf_failure(request, reason=''):
    template = 'core/403csrf.html'
    page_title = 'Доступ запрещен'
    context = {
        'page_title': page_title,
    }
    return render(request, template, context)


def permission_denied(request, exception):
    template = 'core/403.html'
    page_title = 'Доступ запрещен'
    context = {
        'page_title': page_title,
    }
    return render(request, template, context, status=403)


def page_not_found(request, exception):
    template = 'core/404.html'
    page_title = 'Страница не найдена'
    context = {
        'page_title': page_title,
        'path': request.path
    }
    return render(request, template, context, status=404)


def server_error(request):
    template = 'core/500.html'
    page_title = 'Ошибка сервера'
    context = {
        'page_title': page_title,
    }
    return render(request, template, context, status=500)
