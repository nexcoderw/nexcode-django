from home.forms import *
from home.models import *
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

def signIn(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'admin/auth/login.html', context)

def dashboard(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'admin/dashboard.html', context)

def clients(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, "admin/clients/index.html", context)

def clientDetails(request, id):
    settings = Setting.objects.first()

    context = {
        'settings': settings,
        "id": id
    }

    return render(request, "admin/clients/show.html", context)

def updateClient(request, id):
    settings = Setting.objects.first()

    context = {
        'settings': settings,
        "id": id
    }

    return render(request, "admin/clients/edit.html", context)

def deleteClient(request, id):
    pass

def team(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, "admin/members/index.html", context)

def memberDetails(request, id):
    settings = Setting.objects.first()

    context = {
        'settings': settings,
        "id": id
    }

    return render(request, "admin/members/show.html", context)

def updateMember(request, id):
    settings = Setting.objects.first()

    context = {
        'settings': settings,
        "id": id
    }

    return render(request, "admin/members/edit.html", context)

def deleteMember(request, id):
    pass

def projects(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, "admin/projects/index.html", context)