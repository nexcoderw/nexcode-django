from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from home.sitemaps import public_sitemap
from home.views import healthcheck, robots

urlpatterns = [
    path("robots.txt", robots, name="robots"),
    path("sitemap.xml", public_sitemap, name="sitemap"),
    path("health/", healthcheck, name="healthcheck"),
    path("", include("home.urls")),
    path("admin/", admin.site.urls),
    path("ckeditor/", include("ckeditor_uploader.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
