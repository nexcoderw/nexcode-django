from django.urls import include, path


app_name = "admin_api"

urlpatterns = [
    path("auth/", include("admin_api.auth_urls")),
]