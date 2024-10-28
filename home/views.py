from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services/index.html')

def softwareDev(request):
    return render(request, 'services/softwareDev.html')

def uiUx(request):
    return render(request, 'services/uiUx.html')

def digitalMarketing(request):
    return render(request, 'services/digitalMarketing.html')

def mobileDev(request):
    return render(request, 'services/mobileDev.html')

def portfolio(request):
    return render(request, 'portfolio.html')

def team(request):
    return render(request, 'team.html')

def blog(request):
    return render(request, 'blog.html')

def contact(request):
    return render(request, 'contact.html')