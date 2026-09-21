from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from home import views

app_name = "base"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("services/software-development/", views.service_page, name="softwareDev"),
    path("services/ui-ux/", views.service_page, name="uiUx"),
    path("services/digital-marketing/", views.service_page, name="digitalMarketing"),
    path("services/mobile-development/", views.service_page, name="mobileDev"),
    path("services/networking/", views.service_page, name="networking"),
    path("services/maintenance/", views.service_page, name="maintenance"),
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
