import re 
from home.forms import *
from home.models import *
from django.db.models import Q
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    """List, search, and paginate all Client records (newest first)."""
    settings = Setting.objects.first()

    # 1️⃣  Search --------------------------------------------------------
    query = request.GET.get("q", "").strip()
    client_qs = Client.objects.all().order_by("-created_at")               # latest first

    if query:
        client_qs = client_qs.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query)
        )

    # 2️⃣  Pagination ----------------------------------------------------
    paginator = Paginator(client_qs, 10)                                   # 10 per page
    page = request.GET.get("page", 1)

    try:
        clients_page = paginator.page(page)
    except PageNotAnInteger:
        clients_page = paginator.page(1)
    except EmptyPage:
        clients_page = paginator.page(paginator.num_pages)

    # 3️⃣  Context & render ---------------------------------------------
    context = {
        "settings": settings,
        "clients": clients_page,        # iterable in the template
        "paginator": paginator,         # so you can show page numbers
        "query": query,                 # keep the search box filled
    }

    return render(request, "admin/clients/index.html", context)

def addClient(request):
    """
    Create a new Client with solid server-side validation.
    Shows granular error feedback and success toast via Django messages.
    """
    settings = Setting.objects.first()
    errors   = {}

    if request.method == "POST":
        name   = request.POST.get("name", "").strip()
        email  = request.POST.get("email", "").strip()
        phone  = request.POST.get("phone", "").strip()

        # ---- Validation --------------------------------------------------
        if not name:
            errors["name"] = "Client name is required."

        if not email:
            errors["email"] = "Email address is required."
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors["email"] = "Enter a valid email address."

        if not phone:
            errors["phone"] = "Phone number is required."
        elif not re.fullmatch(r"^\+?\d{7,15}$", phone):
            errors["phone"] = "Phone number must contain 7–15 digits (optionally leading ‘+’)."

        # Unique-email guard
        if email and not errors.get("email") and Client.objects.filter(email=email).exists():
            errors["email"] = "A client with this email already exists."

        # ---- Create or bounce back --------------------------------------
        if not errors:
            client = Client.objects.create(
                name=name,
                email=email,
                phone_number=phone,
            )
            messages.success(
                request,
                f'Success!  Client “{client.name or client.email}” was created.',
            )
            return redirect("controller:clients")

        messages.error(request, "Please correct the highlighted errors.")

    # GET or POST-with-errors
    context = {
        "settings": settings,
        "errors":   errors,
        "old":      request.POST if request.method == "POST" else {},
    }

    return render(request, "admin/clients/create.html", context)

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

def addMember(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, "admin/members/create.html", context)

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

def addProject(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, "admin/projects/create.html", context)

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

def addBlog(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, "admin/blogs/create.html", context)

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

def addTestimony(request):
    settings = Setting.objects.first()

    context = {
        'settings': settings
    }

    return render(request, "admin/testimonies/create.html", context)

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