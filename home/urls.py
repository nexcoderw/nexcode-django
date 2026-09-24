from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

from home import views

app_name = "base"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    # Retired detail URLs retain permanent redirects for existing bookmarks.
    path(
        "services/software-development/",
        RedirectView.as_view(pattern_name="base:services", permanent=True),
        name="softwareDev",
    ),
    path(
        "services/ui-ux/",
        RedirectView.as_view(pattern_name="base:services", permanent=True),
        name="uiUx",
    ),
    path(
        "services/digital-marketing/",
        RedirectView.as_view(pattern_name="base:services", permanent=True),
        name="digitalMarketing",
    ),
    path(
        "services/mobile-development/",
        RedirectView.as_view(pattern_name="base:services", permanent=True),
        name="mobileDev",
    ),
    path(
        "services/networking/",
        RedirectView.as_view(pattern_name="base:services", permanent=True),
        name="networking",
    ),
    path(
        "services/maintenance/",
        RedirectView.as_view(pattern_name="base:services", permanent=True),
        name="maintenance",
    ),
    path("portfolio/", views.removed_content),
    path("work/<slug>", views.removed_content),
    path("team/", views.team, name="team"),
    # Member detail pages are retired; old links land on the team page.
    # A fixed url, not pattern_name: pattern_name would pass the captured
    # slug to reverse(), and the team route takes no slug.
    path(
        "team/<slug>/",
        RedirectView.as_view(url=reverse_lazy("base:team"), permanent=True),
    ),
    path("blogs/", views.removed_content),
    path("blog/<slug>/", views.removed_content),
    path("testimony/", views.removed_content),
    path("training/", views.removed_content),
    path("training/<slug:slug>/", views.removed_content),
    path("contact/", views.contact, name="contact"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
