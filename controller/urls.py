from controller.views import *
from django.conf import settings
from django.urls import path, re_path
from django.conf.urls.static import static

app_name = 'admin'

urlpatterns = [
    path('', signIn, name="signIn"),

    path('dashboard/', dashboard, name="dashboard"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
