from home.forms import *
from home.models import *
from django.contrib import messages
from django.shortcuts import render, redirect

def home(request):
    portfolio = Portfolio.objects.all()[:4]
    team = Team.objects.all()[:4]
    settings = Setting.objects.first()

    context = {
        'portfolio': portfolio,
        'team': team,
        'settings': settings
    }

    return render(request, 'index.html', context)

def about(request):
    team = Team.objects.all()
    settings = Setting.objects.first()

    context = {
        'team': team,
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
    portfolio = Portfolio.objects.all().order_by('-created_at')
    settings = Setting.objects.first()

    context = {
        'portfolio': portfolio,
        'settings': settings
    }

    return render(request, 'portfolio.html', context)

def team(request):
    team = Team.objects.all()
    settings = Setting.objects.first()

    context = {
        'team': team,
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
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the form data to the database
            contact_message = form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('base:contact')
        else:
            messages.error(request, 'There was an error submitting your message. Please try again.')
    else:
        form = ContactForm()

    settings = Setting.objects.first()

    context = {
        'form': form,
        'settings': settings
    }

    return render(request, 'contact.html', context)