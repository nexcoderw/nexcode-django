from home.models import *
from controller.forms import *
from controller.decorators import *
from django.contrib import messages
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay
from django.contrib.auth.decorators import login_required
from django.db.models import Q, ProtectedError, Count, Sum
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def signIn(request):
    settings = Setting.objects.first()

    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if not email or not password:
            messages.error(request, "❌ Please enter both email and password.")
            return render(request, 'admin/auth/login.html', {'settings': settings})

        # Try to find the user by email (because default User uses username)
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user = None

        if user is not None:
            # Check password and superuser status
            user_auth = authenticate(request, username=user.username, password=password)
            if user_auth is not None:
                if user_auth.is_superuser:
                    login(request, user_auth)
                    messages.success(request, f"✅ Welcome back, Superadmin {user_auth.username}!")
                    return redirect('controller:dashboard')
                else:
                    messages.error(request, "❌ Access denied: You must be a superadmin to log in here.")
            else:
                messages.error(request, "❌ Invalid credentials. Please check your email and password.")
        else:
            messages.error(request, "❌ No user found with this email address.")

    return render(request, 'admin/auth/login.html', {'settings': settings})

def signOut(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "✅ You have been logged out successfully.")
    else:
        messages.info(request, "ℹ️ You were not logged in.")
    return redirect('controller:signIn')

@superuser_required
def dashboard(request):
    settings = Setting.objects.first()

    # Date filter inputs (defaults: last 30 days)
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else datetime.today().date() - timedelta(days=30)
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else datetime.today().date()
    except ValueError:
        start_date = datetime.today().date() - timedelta(days=30)
        end_date = datetime.today().date()

    # Filter querysets by date range (created_at between start_date and end_date)
    clients = Client.objects.filter(created_at__date__range=(start_date, end_date))
    projects = Portfolio.objects.filter(created_at__date__range=(start_date, end_date))
    blogs = Blog.objects.filter(published_at__date__range=(start_date, end_date))
    testimonies = Testimony.objects.filter(created_at__date__range=(start_date, end_date))
    trainings = Training.objects.filter(start_date__range=(start_date, end_date))
    contacts = Contact.objects.filter(created_at__date__range=(start_date, end_date))

    # Aggregate counts and sums
    total_clients = clients.count()
    total_projects = projects.count()
    total_blogs = blogs.count()
    total_testimonies = testimonies.count()
    total_trainings = trainings.count()
    total_contacts = contacts.count()

    # Payment stats for projects in the date range
    total_project_amount = projects.aggregate(total=Sum('project_amount'))['total'] or 0
    total_amount_paid = projects.aggregate(total=Sum('amount_paid'))['total'] or 0

    # Prepare data for charts - Daily new clients/projects/blogs over date range
    def daily_counts(qs, date_field):
        daily_data = qs.annotate(day=TruncDay(date_field)).values('day').annotate(count=Count('id')).order_by('day')
        dates = []
        counts = []
        current_day = start_date
        while current_day <= end_date:
            dates.append(current_day.strftime('%Y-%m-%d'))
            match = next((item for item in daily_data if item['day'].date() == current_day), None)
            counts.append(match['count'] if match else 0)
            current_day += timedelta(days=1)
        return dates, counts

    clients_dates, clients_counts = daily_counts(clients, 'created_at')
    projects_dates, projects_counts = daily_counts(projects, 'created_at')
    blogs_dates, blogs_counts = daily_counts(blogs, 'published_at')

    # Recent activities (latest 5 each)
    recent_clients = clients.order_by('-created_at')[:5]
    recent_projects = projects.order_by('-created_at')[:5]
    recent_blogs = blogs.order_by('-published_at')[:5]
    recent_contacts = contacts.order_by('-created_at')[:5]

    context = {
        'settings': settings,
        'total_clients': total_clients,
        'total_projects': total_projects,
        'total_blogs': total_blogs,
        'total_testimonies': total_testimonies,
        'total_trainings': total_trainings,
        'total_contacts': total_contacts,
        'total_project_amount': total_project_amount,
        'total_amount_paid': total_amount_paid,

        'clients_dates': clients_dates,
        'clients_counts': clients_counts,
        'projects_dates': projects_dates,
        'projects_counts': projects_counts,
        'blogs_dates': blogs_dates,
        'blogs_counts': blogs_counts,

        'recent_clients': recent_clients,
        'recent_projects': recent_projects,
        'recent_blogs': recent_blogs,
        'recent_contacts': recent_contacts,

        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }

    return render(request, 'admin/dashboard.html', context)

@superuser_required
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

@superuser_required
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

@superuser_required
def clientDetails(request, id):
    settings = Setting.objects.first()

    context = {
        'settings': settings,
        "id": id
    }

    return render(request, "admin/clients/show.html", context)

@superuser_required
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

@superuser_required
def deleteClient(request, id):
    """
    Permanently remove a Client record.

    • Executes instantly (link is GET-based).  
    • Catches FK-protected rows and informs the user.  
    • Always redirects back to the client list.
    """
    client = get_object_or_404(Client, pk=id)
    client_label = client.name or client.email or f"ID {client.pk}"

    try:
        client.delete()
        messages.success(request, f"🗑️ Client “{client_label}” deleted successfully.")
    except ProtectedError:
        messages.error(
            request,
            f"❌ Client “{client_label}” can’t be removed because it’s referenced by other records."
        )

    return redirect("controller:clients")

@superuser_required
def team(request):
    settings = Setting.objects.first()

    query = request.GET.get("q", "").strip()
    team_qs = Team.objects.all().order_by("-created_at")  # newest first

    if query:
        team_qs = team_qs.filter(
            Q(name__icontains=query) |
            Q(position__icontains=query)
        )

    paginator = Paginator(team_qs, 10)
    page = request.GET.get("page", 1)

    try:
        team_page = paginator.page(page)
    except PageNotAnInteger:
        team_page = paginator.page(1)
    except EmptyPage:
        team_page = paginator.page(paginator.num_pages)

    context = {
        "settings": settings,
        "teams": team_page,
        "paginator": paginator,
        "query": query,
    }

    return render(request, "admin/members/index.html", context)

@superuser_required
def addMember(request):
    settings = Setting.objects.first()

    if request.method == "POST":
        form = TeamForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save()
            messages.success(request, f"✅ Team member “{member.name or 'Unnamed'}” created successfully.")
            return redirect("controller:team")
        else:
            messages.error(request, "❌ Could not save the member. Please correct the errors below.")
    else:
        form = TeamForm()

    context = {
        "settings": settings,
        "form": form,
    }

    return render(request, "admin/members/create.html", context)

@superuser_required
def memberDetails(request, id):
    settings = Setting.objects.first()
    member = get_object_or_404(Team, pk=id)

    context = {
        "settings": settings,
        "member": member,
    }

    return render(request, "admin/members/show.html", context)

@superuser_required
def updateMember(request, id):
    settings = Setting.objects.first()
    member = get_object_or_404(Team, pk=id)

    if request.method == "POST":
        form = TeamForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Team member “{member.name or 'Unnamed'}” updated successfully.")
            return redirect("controller:team")
        else:
            messages.error(request, "❌ Could not update the member. Please fix the errors below.")
    else:
        form = TeamForm(instance=member)

    context = {
        "settings": settings,
        "form": form,
        "member": member,
    }

    return render(request, "admin/members/edit.html", context)

@superuser_required
def deleteMember(request, id):
    member = get_object_or_404(Team, pk=id)
    member_label = member.name or f"ID {member.pk}"

    try:
        member.delete()
        messages.success(request, f"🗑️ Team member “{member_label}” deleted successfully.")
    except ProtectedError:
        messages.error(request, f"❌ Team member “{member_label}” can't be deleted because it is referenced by other records.")

    return redirect("controller:team")

@superuser_required
def projects(request):
    settings = Setting.objects.first()

    query = request.GET.get("q", "").strip()
    portfolio_qs = Portfolio.objects.all().order_by("-created_at")

    if query:
        portfolio_qs = portfolio_qs.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )

    paginator = Paginator(portfolio_qs, 12)
    page = request.GET.get("page", 1)

    try:
        portfolios = paginator.page(page)
    except PageNotAnInteger:
        portfolios = paginator.page(1)
    except EmptyPage:
        portfolios = paginator.page(paginator.num_pages)

    context = {
        "settings": settings,
        "portfolios": portfolios,
        "paginator": paginator,
        "query": query,
    }

    return render(request, "admin/projects/index.html", context)

@superuser_required
def addProject(request):
    settings = Setting.objects.first()

    if request.method == "POST":
        form = PortfolioForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()
            messages.success(request, f"✅ Project “{project.name or 'Unnamed'}” created successfully.")
            return redirect("controller:projects")
        else:
            messages.error(request, "❌ Could not save the project. Please correct the errors below.")
    else:
        form = PortfolioForm()

    context = {
        "settings": settings,
        "form": form,
    }

    return render(request, "admin/projects/create.html", context)

@superuser_required
def projectDetails(request, id):
    settings = Setting.objects.first()
    project = get_object_or_404(Portfolio, pk=id)

    context = {
        "settings": settings,
        "project": project,
    }

    return render(request, "admin/projects/show.html", context)

@superuser_required
def updateProject(request, id):
    settings = Setting.objects.first()
    project = get_object_or_404(Portfolio, pk=id)

    if request.method == "POST":
        form = PortfolioForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Project “{project.name or 'Unnamed'}” updated successfully.")
            return redirect("controller:projects")
        else:
            messages.error(request, "❌ Could not update the project. Please fix the errors below.")
    else:
        form = PortfolioForm(instance=project)

    context = {
        "settings": settings,
        "form": form,
        "project": project,
    }

    return render(request, "admin/projects/edit.html", context)

@superuser_required
def deleteProject(request, id):
    project = get_object_or_404(Portfolio, pk=id)
    project_label = project.name or f"ID {project.pk}"

    try:
        project.delete()
        messages.success(request, f"🗑️ Project “{project_label}” deleted successfully.")
    except ProtectedError:
        messages.error(request, f"❌ Project “{project_label}” can’t be deleted because it is referenced by other records.")

    return redirect("controller:projects")

@superuser_required
def blogs(request):
    settings = Setting.objects.first()

    query = request.GET.get("q", "").strip()
    blog_qs = Blog.objects.all().order_by("-published_at", "-created_at")

    if query:
        blog_qs = blog_qs.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(category__icontains=query)
        )

    paginator = Paginator(blog_qs, 10)
    page = request.GET.get("page", 1)

    try:
        blogs_page = paginator.page(page)
    except PageNotAnInteger:
        blogs_page = paginator.page(1)
    except EmptyPage:
        blogs_page = paginator.page(paginator.num_pages)

    context = {
        "settings": settings,
        "blogs": blogs_page,
        "paginator": paginator,
        "query": query,
    }

    return render(request, "admin/blogs/index.html", context)

@superuser_required
def addBlog(request):
    settings = Setting.objects.first()

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            form.save_m2m()  # For tags
            messages.success(request, f"✅ Blog “{blog.title or 'Untitled'}” created successfully.")
            return redirect("controller:blogs")
        else:
            messages.error(request, "❌ Could not save the blog. Please correct the errors below.")
    else:
        form = BlogForm()

    context = {
        "settings": settings,
        "form": form,
    }

    return render(request, "admin/blogs/create.html", context)

@superuser_required
def blogDetails(request, id):
    settings = Setting.objects.first()
    blog = get_object_or_404(Blog, pk=id)

    context = {
        "settings": settings,
        "blog": blog,
    }

    return render(request, "admin/blogs/show.html", context)

@superuser_required
def updateBlog(request, id):
    settings = Setting.objects.first()
    blog = get_object_or_404(Blog, pk=id)

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Blog “{blog.title or 'Untitled'}” updated successfully.")
            return redirect("controller:blogs")
        else:
            messages.error(request, "❌ Could not update the blog. Please fix the errors below.")
    else:
        form = BlogForm(instance=blog)

    context = {
        "settings": settings,
        "form": form,
        "blog": blog,
    }

    return render(request, "admin/blogs/edit.html", context)

@superuser_required
def deleteBlog(request, id):
    blog = get_object_or_404(Blog, pk=id)
    blog_label = blog.title or f"ID {blog.pk}"

    try:
        blog.delete()
        messages.success(request, f"🗑️ Blog “{blog_label}” deleted successfully.")
    except ProtectedError:
        messages.error(request, f"❌ Blog “{blog_label}” can’t be deleted because it is referenced by other records.")

    return redirect("controller:blogs")

@superuser_required
def testimonies(request):
    settings = Setting.objects.first()

    query = request.GET.get("q", "").strip()
    testimony_qs = Testimony.objects.select_related('client').all().order_by("-created_at")

    if query:
        testimony_qs = testimony_qs.filter(
            Q(message__icontains=query) |
            Q(client__name__icontains=query)
        )

    paginator = Paginator(testimony_qs, 10)
    page = request.GET.get("page", 1)

    try:
        testimonies_page = paginator.page(page)
    except PageNotAnInteger:
        testimonies_page = paginator.page(1)
    except EmptyPage:
        testimonies_page = paginator.page(paginator.num_pages)

    context = {
        "settings": settings,
        "testimonies": testimonies_page,
        "paginator": paginator,
        "query": query,
    }

    return render(request, "admin/testimonies/index.html", context)

@superuser_required
def addTestimony(request):
    settings = Setting.objects.first()

    if request.method == "POST":
        form = TestimonyForm(request.POST)
        if form.is_valid():
            testimony = form.save()
            messages.success(request, f"✅ Testimony from “{testimony.client.name if testimony.client else 'Anonymous'}” created successfully.")
            return redirect("controller:testimonies")
        else:
            messages.error(request, "❌ Could not save the testimony. Please fix the errors below.")
    else:
        form = TestimonyForm()

    context = {
        "settings": settings,
        "form": form,
    }

    return render(request, "admin/testimonies/create.html", context)

@superuser_required
def testimonyDetails(request, id):
    settings = Setting.objects.first()
    testimony = get_object_or_404(Testimony, pk=id)

    context = {
        "settings": settings,
        "testimony": testimony,
    }

    return render(request, "admin/testimonies/show.html", context)

@superuser_required
def updateTestimony(request, id):
    settings = Setting.objects.first()
    testimony = get_object_or_404(Testimony, pk=id)

    if request.method == "POST":
        form = TestimonyForm(request.POST, instance=testimony)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Testimony from “{testimony.client.name if testimony.client else 'Anonymous'}” updated successfully.")
            return redirect("controller:testimonies")
        else:
            messages.error(request, "❌ Could not update the testimony. Please fix the errors below.")
    else:
        form = TestimonyForm(instance=testimony)

    context = {
        "settings": settings,
        "form": form,
        "testimony": testimony,
    }

    return render(request, "admin/testimonies/edit.html", context)

@superuser_required
def deleteTestimony(request, id):
    testimony = get_object_or_404(Testimony, pk=id)
    label = testimony.client.name if testimony.client else f"ID {testimony.pk}"

    try:
        testimony.delete()
        messages.success(request, f"🗑️ Testimony from “{label}” deleted successfully.")
    except ProtectedError:
        messages.error(request, f"❌ Testimony from “{label}” cannot be deleted because it is referenced by other records.")

    return redirect("controller:testimonies")

@superuser_required
def trainings(request):
    settings = Setting.objects.first()

    query = request.GET.get("q", "").strip()
    trainings_qs = Training.objects.all().order_by("-start_date")

    if query:
        trainings_qs = trainings_qs.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(status__icontains=query)
        )

    paginator = Paginator(trainings_qs, 10)
    page = request.GET.get("page", 1)

    try:
        trainings_page = paginator.page(page)
    except PageNotAnInteger:
        trainings_page = paginator.page(1)
    except EmptyPage:
        trainings_page = paginator.page(paginator.num_pages)

    context = {
        "settings": settings,
        "trainings": trainings_page,
        "paginator": paginator,
        "query": query,
    }

    return render(request, "admin/trainings/index.html", context)

@superuser_required
def addTraining(request):
    settings = Setting.objects.first()

    if request.method == "POST":
        form = TrainingForm(request.POST, request.FILES)
        if form.is_valid():
            training = form.save()
            messages.success(request, f"✅ Training “{training.title}” created successfully.")
            return redirect("controller:trainings")
        else:
            messages.error(request, "❌ Could not create training. Please fix the errors below.")
    else:
        form = TrainingForm()

    context = {
        "settings": settings,
        "form": form,
    }

    return render(request, "admin/trainings/create.html", context)

@superuser_required
def trainingDetails(request, id):
    settings = Setting.objects.first()
    training = get_object_or_404(Training, pk=id)

    context = {
        "settings": settings,
        "training": training,
    }

    return render(request, "admin/trainings/show.html", context)

@superuser_required
def updateTraining(request, id):
    settings = Setting.objects.first()
    training = get_object_or_404(Training, pk=id)

    if request.method == "POST":
        form = TrainingForm(request.POST, request.FILES, instance=training)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Training “{training.title}” updated successfully.")
            return redirect("controller:trainings")
        else:
            messages.error(request, "❌ Could not update training. Please fix the errors below.")
    else:
        form = TrainingForm(instance=training)

    context = {
        "settings": settings,
        "form": form,
        "training": training,
    }

    return render(request, "admin/trainings/edit.html", context)

@superuser_required
def deleteTraining(request, id):
    training = get_object_or_404(Training, pk=id)
    label = training.title

    try:
        training.delete()
        messages.success(request, f"🗑️ Training “{label}” deleted successfully.")
    except ProtectedError:
        messages.error(request, f"❌ Training “{label}” cannot be deleted because it is referenced by other records.")

    return redirect("controller:trainings")

@superuser_required
def contacts(request):
    settings = Setting.objects.first()

    query = request.GET.get("q", "").strip()
    contact_qs = Contact.objects.all().order_by("-created_at")

    if query:
        contact_qs = contact_qs.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(subject__icontains=query) |
            Q(message__icontains=query)
        )

    paginator = Paginator(contact_qs, 10)
    page = request.GET.get("page", 1)

    try:
        contacts_page = paginator.page(page)
    except PageNotAnInteger:
        contacts_page = paginator.page(1)
    except EmptyPage:
        contacts_page = paginator.page(paginator.num_pages)

    context = {
        "settings": settings,
        "contacts": contacts_page,
        "paginator": paginator,
        "query": query,
    }

    return render(request, "admin/contacts/index.html", context)