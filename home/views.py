from home.forms import *
from home.models import *
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
def home(request):
    portfolio = Portfolio.objects.filter(publish=True, project_category='Client Project').order_by('-created_at')[:4]
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

    return render(request, 'services/software-development.html', context)

def uiUx(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'services/ui-ux.html', context)

def digitalMarketing(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'services/digital-marketing.html', context)

def mobileDev(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'services/mobile-development.html', context)

def networking(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'services/networking.html', context)

def maintenance(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, 'services/maintenance.html', context)

def portfolio(request):
    portfolio = Portfolio.objects.filter(publish=True, project_category='Client Project').order_by('-created_at')
    settings = Setting.objects.first()

    context = {
        'portfolio': portfolio,
        'settings': settings
    }

    return render(request, 'work/index.html', context)

def workDetails(request, slug):
    work = get_object_or_404(Portfolio, slug=slug)
    settings = Setting.objects.first()
    recentWork = Portfolio.objects.all().order_by('-created_at')[:3]
    recentBlog = Blog.objects.filter(status='Published').order_by('-created_at')[:3]

    context = {
        'work': work,
        'settings': settings,
        'recentWork': recentWork,
        'recentBlog': recentBlog
    }

    return render(request, 'work/show.html', context)

def team(request):
    team = Team.objects.all()
    settings = Setting.objects.first()

    context = {
        'team': team,
        'settings': settings
    }

    return render(request, 'team/index.html', context)

def getTeamMember(request, slug):
    member = get_object_or_404(Team, slug=slug)
    settings = Setting.objects.first()
    
    portfolios = Portfolio.objects.filter(team_members=member).order_by('-created_at')

    context = {
        'member': member,
        'settings': settings,
        'portfolios': portfolios,  # Send portfolios to the template
    }

    return render(request, 'team/show.html', context)

def blogs(request):
    blogs = Blog.objects.all().order_by('-created_at')
    settings = Setting.objects.first()

    for blog in blogs:
        blog.created_at_iso = blog.created_at.isoformat()

    context = {
        'blogs': blogs,
        'settings': settings
    }

    return render(request, 'blogs/index.html', context)

def getBlogDetails(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    settings = Setting.objects.first()

    blog.created_at_iso = blog.created_at.isoformat()
    if blog.published_at:
        blog.published_at_iso = blog.published_at.isoformat()
    else:
        blog.published_at_iso = None

    context = {
        'blog': blog,
        'settings': settings
    }

    return render(request, 'blogs/show.html', context)

def addTestimony(request):
    settings = Setting.objects.first()
    if request.method == 'POST':
        form = TestimonyForm(request.POST, request.FILES)
        if form.is_valid():
            # Extract cleaned form data
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            phone_number = form.cleaned_data.get('phone_number')
            image = form.cleaned_data.get('image')
            message_text = form.cleaned_data.get('message')
            
            # Check if a client with the provided email or phone number exists
            client = Client.objects.filter(Q(email=email) | Q(phone_number=phone_number)).first()
            if not client:
                # Create a new Client record if not found
                client = Client.objects.create(
                    name=name,
                    email=email,
                    phone_number=phone_number,
                    image=image
                )
            
            # Create a new Testimony record linked to the client
            Testimony.objects.create(
                client=client,
                message=message_text
            )
            
            messages.success(request, "Your testimony has been submitted successfully!")
            return redirect('base:addTestimony')
        else:
            messages.error(request, "There was an error submitting your testimony. Please check the form and try again.")
    else:
        form = TestimonyForm()
        
    context = {
        'form': form,
        'settings': settings
    }
    return render(request, 'testimony.html', context)

def getTraining(request):
    settings = Setting.objects.first()

    trainings_qs = Training.objects.all().order_by('-start_date')

    paginator = Paginator(trainings_qs, 12)
    page = request.GET.get('page', 1)

    try:
        trainings_page = paginator.page(page)
    except PageNotAnInteger:
        trainings_page = paginator.page(1)
    except EmptyPage:
        trainings_page = paginator.page(paginator.num_pages)

    context = {
        'settings': settings,
        'trainings': trainings_page,
        'paginator': paginator,
    }

    return render(request, 'training/index.html', context)

def trainingDetail(request, slug):
    settings = Setting.objects.first()
    training = get_object_or_404(Training, slug=slug)

    context = {
        'settings': settings,
        'training': training,
    }

    return render(request, 'training/show.html', context)

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