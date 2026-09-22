from django.conf import settings
from django.contrib import messages
from django.core.paginator import InvalidPage, Paginator
from django.db import connection
from django.http import Http404, HttpResponse, HttpResponseGone, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_safe

from home.content import SERVICES
from home.forms import ContactForm
from home.models import Team
from home.seo import render_page


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
    return render_page(request, "index.html", {"services": SERVICES})


def about(request):
    return render_page(request, "about.html", {"team": Team.objects.all()})


def services(request):
    return render_page(request, "services/index.html", {"services": SERVICES})


def team(request):
    page = page_for(request, Team.objects.order_by("name", "pk"))
    return render_page(request, "team/index.html", {"team": page, "page_obj": page})


def getTeamMember(request, slug):
    member = get_object_or_404(Team, slug=slug)
    return render_page(
        request,
        "team/show.html",
        {"member": member},
        title=f"{member.name} — {member.position or 'Team'}",
        description=f"Meet {member.name}, {member.position or 'a team member'} at NEXCODE.",
        image=member.image.url if member.image else None,
    )


@require_safe
def removed_content(request, slug=None):
    return HttpResponseGone("This page is no longer available.")


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
