from home.views import *
from django.conf import settings
from django.urls import path, re_path
from django.conf.urls.static import static

app_name = 'base'

urlpatterns = [
    path('', home, name="home"),
    path('about/', about, name="about"),
    path('services/', services, name="services"),
    path('services/software-development/', softwareDev, name="softwareDev"),
    path('services/ui-ux/', uiUx, name="uiUx"),
    path('services/digital-marketing/', digitalMarketing, name="digitalMarketing"),
    path('services/mobile-development/', mobileDev, name="mobileDev"),
    path('portfolio/', portfolio, name="portfolio"),
    path('work/<slug>', workDetails, name="workDetails"),
    path('team/', team, name="team"),
    path('blogs/', blogs, name="blogs"),
    path('blog/<slug>/', getBlogDetails, name="getBlogDetails"),
    path('contact/', contact, name="contact"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
