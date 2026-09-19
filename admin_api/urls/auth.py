from django.urls import path

from admin_api import views


app_name = "auth"

urlpatterns = [
    path(
        "csrf/",
        views.csrf_token_view,
        name="csrf",
    ),
    path(
        "login/",
        views.login_view,
        name="login",
    ),
]