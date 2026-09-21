from django.conf import settings
from django.contrib import messages
from django.core.paginator import InvalidPage, Paginator
from django.db import connection, transaction
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_safe

from home.content import SERVICES
from home.forms import ContactForm, TestimonyForm
from home.models import Blog, Client, Portfolio, Team, Testimony, Training
from home.seo import plain_text, render_page


def public_projects():
    return Portfolio.objects.filter(publish=True).order_by("-created_at", "-pk")


def published_blogs():
    # A future publication date must not expose an article before its release.
    return (
        Blog.objects.filter(status="Published")
        .filter(Q(published_at__lte=timezone.now()) | Q(published_at__isnull=True))
        .order_by("-published_at", "-created_at", "-pk")
    )


def page_for(request, queryset, per_page=12):
    try:
        return Paginator(queryset, per_page).page(request.GET.get("page", 1))
    except InvalidPage as error:
        raise Http404("This page does not exist.") from error


def healthcheck(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        # Health probes must return a stable response without exposing database details.
        return JsonResponse({"status": "error", "database": "unavailable"}, status=503)
    return JsonResponse({"status": "ok", "database": "ok"})


def home(request):
    projects = (
        public_projects()
        .filter(project_category="Client Project")
        .prefetch_related("images")[:4]
    )
    return render_page(
        request, "index.html", {"portfolio": projects, "services": SERVICES}
    )


def about(request):
    return render_page(request, "about.html", {"team": Team.objects.all()})


def services(request):
    return render_page(request, "services/index.html", {"services": SERVICES})


def service_page(request):
    service = SERVICES[request.resolver_match.url_name]
    return render_page(
        request, f"services/{service['slug']}.html", {"service": service}
    )


def portfolio(request):
    page = page_for(
        request,
        public_projects()
        .filter(project_category="Client Project")
        .prefetch_related("images"),
    )
    return render_page(
        request, "work/index.html", {"portfolio": page, "page_obj": page}
    )


def workDetails(request, slug):
    work = get_object_or_404(public_projects().prefetch_related("images"), slug=slug)
    images = list(work.images.all())
    return render_page(
        request,
        "work/show.html",
        {"work": work, "images": images},
        title=f"{work.name} — Project",
        description=plain_text(work.description)
        or f"Explore {work.name}, a published NEXCODE project.",
        image=images[0].image.url if images else None,
    )


def team(request):
    page = page_for(request, Team.objects.order_by("name", "pk"))
    return render_page(request, "team/index.html", {"team": page, "page_obj": page})


def getTeamMember(request, slug):
    member = get_object_or_404(Team, slug=slug)
    page = page_for(
        request,
        public_projects().filter(team_members=member).prefetch_related("images"),
    )
    return render_page(
        request,
        "team/show.html",
        {"member": member, "portfolio": page, "portfolios": page, "page_obj": page},
        title=f"{member.name} — {member.position or 'Team'}",
        description=f"Meet {member.name}, {member.position or 'a team member'} at NEXCODE. Explore their published projects and professional profiles.",
        image=member.image.url if member.image else None,
    )


def blogs(request):
    page = page_for(request, published_blogs().select_related("author"))
    return render_page(request, "blogs/index.html", {"blogs": page, "page_obj": page})


def getBlogDetails(request, slug):
    blog = get_object_or_404(
        published_blogs().select_related("author").prefetch_related("tags"), slug=slug
    )
    return render_page(
        request,
        "blogs/show.html",
        {"blog": blog},
        title=blog.title,
        description=plain_text(blog.excerpt or blog.content),
        image=blog.featured_image.url if blog.featured_image else None,
        article=blog,
    )


def addTestimony(request):
    form = TestimonyForm(
        request.POST if request.method == "POST" else None, request.FILES or None
    )
    if request.method == "POST":
        if form.is_valid():
            with transaction.atomic():
                client = Client.objects.filter(
                    Q(email=form.cleaned_data["email"])
                    | Q(phone_number=form.cleaned_data["phone_number"])
                ).first()
                if client is None:
                    client = Client.objects.create(
                        **{
                            key: form.cleaned_data[key]
                            for key in ("name", "email", "phone_number", "image")
                        }
                    )
                Testimony.objects.create(
                    client=client, message=form.cleaned_data["message"]
                )
            messages.success(request, "Thank you. Your feedback has been received.")
            return redirect("base:addTestimony")
        messages.error(
            request, "Your feedback has not been sent. Check the fields marked below."
        )
    return render_page(request, "testimony.html", {"form": form})


def getTraining(request):
    page = page_for(request, Training.objects.order_by("-start_date", "-pk"))
    return render_page(
        request, "training/index.html", {"trainings": page, "page_obj": page}
    )


def trainingDetail(request, slug):
    training = get_object_or_404(Training, slug=slug)
    return render_page(
        request,
        "training/show.html",
        {"training": training},
        title=training.title,
        description=plain_text(training.description),
        image=training.image.url if training.image else None,
    )


def contact(request):
    initial = {"subject": request.GET.get("service", "")[:150]}
    form = ContactForm(
        request.POST if request.method == "POST" else None, initial=initial
    )
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your message has been received. Our team will reply using the email address you provided.",
            )
            return redirect("base:contact")
        messages.error(
            request, "Your message has not been sent. Check the fields marked below."
        )
    return render_page(request, "contact.html", {"form": form})


@require_safe
def robots(request):
    # Let crawlers read noindex directives on non-production pages.
    lines = ["User-agent: *", "Allow: /"]
    if settings.SEARCH_ENGINE_INDEXING:
        lines.append(f"Sitemap: {settings.SITE_URL}/sitemap.xml")
    response = HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
    if not settings.SEARCH_ENGINE_INDEXING:
        response["X-Robots-Tag"] = "noindex, follow"
    return response
