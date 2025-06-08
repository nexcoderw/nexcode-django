from home.models import *
from controller.forms import *
from django.db.models import Q
from django.contrib import messages
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
    """Create a new Client with full validation & rich feedback."""
    settings = Setting.objects.first()

    if request.method == "POST":
        form = ClientForm(request.POST, request.FILES)
        if form.is_valid():
            client = form.save()
            messages.success(
                request,
                f"✅ Client “{client.name or client.email}” was created successfully."
            )
            return redirect("controller:clients")
        else:
            # Automatically carries form.errors into the template
            messages.error(
                request,
                "❌ We couldn’t save the client. Please correct the errors below."
            )
    else:
        form = ClientForm()

    context = {
        "settings": settings,
        "form": form,
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
    """Edit an existing Client with rich validations & feedback."""
    settings = Setting.objects.first()
    client   = get_object_or_404(Client, pk=id)

    if request.method == "POST":
        form = ClientForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"✅ Client “{client.name or client.email}” updated successfully."
            )
            return redirect("controller:clients")
        else:
            messages.error(
                request,
                "❌ We couldn’t update the client. Please correct the errors below."
            )
    else:
        form = ClientForm(instance=client)

    context = {
        "settings": settings,
        "form": form,
        "client": client,
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