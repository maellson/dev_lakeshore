from django.shortcuts import render
from django.views.defaults import page_not_found, server_error


def custom_404(request, exception):
    """View customizada para erro 404"""
    return render(request, '404.html', status=404)


def custom_500(request):
    """View customizada para erro 500"""
    return render(request, '500.html', status=500)


def custom_403(request, exception):
    """View customizada para erro 403"""
    return render(request, '403.html', status=403)


def custom_400(request, exception):
    """View customizada para erro 400"""
    return render(request, '400.html', status=400)
