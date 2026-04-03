from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from home.views import healthcheck

urlpatterns = [
    path('health/', healthcheck, name='healthcheck'),
    path('', include('home.urls')),
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
