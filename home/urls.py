from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
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
    path("portfolio/", views.portfolio, name="portfolio"),
    path("work/<slug>", views.workDetails, name="workDetails"),
    path("team/", views.team, name="team"),
    path("team/<slug>/", views.getTeamMember, name="getTeamMember"),
    path("blogs/", views.blogs, name="blogs"),
    path("blog/<slug>/", views.getBlogDetails, name="getBlogDetails"),
    path("testimony/", views.addTestimony, name="addTestimony"),
    path("training/", views.getTraining, name="getTraining"),
    path("training/<slug:slug>/", views.trainingDetail, name="trainingDetail"),
    path("contact/", views.contact, name="contact"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
