from urllib.parse import quote

from django.conf import settings
from django.core.paginator import InvalidPage, Paginator
from django.db import connection
from django.http import Http404, HttpResponse, HttpResponseGone, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_safe

from home.content import SERVICES
from home.models import Team
from home.seo import render_page


# The order set in the admin: lowest display_order first, and members
# sharing a position alphabetically, so the order never shifts between
# page loads.
TEAM_DISPLAY_ORDER = ("display_order", "name", "pk")

# The home page shows one row of the team and links to the full page.
HOME_TEAM_PREVIEW_SIZE = 4


def team_in_display_order():
    return Team.objects.order_by(*TEAM_DISPLAY_ORDER)


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
    return render_page(
        request,
        "index.html",
        {
            "services": SERVICES,
            # The first members in display order, fetched with a LIMIT.
            "team": team_in_display_order()[:HOME_TEAM_PREVIEW_SIZE],
        },
    )


def about(request):
    return render_page(request, "about.html", {"team": team_in_display_order()})


def services(request):
    return render_page(request, "services/index.html", {"services": SERVICES})


def team(request):
    page = page_for(request, team_in_display_order())
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


@require_safe
def contact(request):
    service = request.GET.get("service", "").strip()[:150]
    subject = f"Enquiry about {service}" if service else "NEXCODE enquiry"
    return render_page(
        request, "contact.html", {"email_subject": quote(subject)}
    )


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
