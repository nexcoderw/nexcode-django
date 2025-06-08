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

def projectDetails(request, id):
    settings = Setting.objects.first()

    context = {
        'settings': settings,
        "id": id
    }

    return render(request, "admin/projects/show.html", context)

def updateProject(request, id):
    settings = Setting.objects.first()

    context = {
        'settings': settings,
        "id": id
    }

    return render(request, "admin/projects/edit.html", context)

def deleteProject(request, id):
    pass

def blogs(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, "admin/blogs/index.html", context)

def blogDetails(request, id):
    settings = Setting.objects.first()

    context = {
        'settings': settings,
        "id": id
    }

    return render(request, "admin/blogs/show.html", context)

def updateBlog(request, id):
    settings = Setting.objects.first()

    context = {
        'settings': settings,
        "id": id
    }

    return render(request, "admin/blogs/edit.html", context)

def deleteBlog(request, id):
    pass

def testimonies(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, "admin/testimonies/index.html", context)

def testimonyDetails(request, id):
    settings = Setting.objects.first()

    context = {
        'settings': settings,
        "id": id
    }

    return render(request, "admin/testimonies/show.html", context)

def updateTestimony(request, id):
    settings = Setting.objects.first()

    context = {
        'settings': settings,
        "id": id
    }

    return render(request, "admin/testimonies/edit.html", context)

def deleteTestimony(request, id):
    pass

def contacts(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, "admin/contacts/index.html", context)