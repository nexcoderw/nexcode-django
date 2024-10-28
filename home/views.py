from home.models import *
from django.shortcuts import render

def home(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'index.html', context)

def about(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'about.html', context)

def services(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'services/index.html', context)

def softwareDev(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'services/softwareDev.html', context)

def uiUx(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'services/uiUx.html', context)

def digitalMarketing(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'services/digitalMarketing.html', context)

def mobileDev(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'services/mobileDev.html', context)

def portfolio(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'portfolio.html', context)

def team(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'team.html', context)

def blogs(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'blogs/index.html', context)

def contact(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'contact.html', context)