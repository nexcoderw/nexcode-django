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