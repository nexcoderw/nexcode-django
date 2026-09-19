from django.urls import path

from admin_api.views import auth


app_name = "auth"

urlpatterns = [
    path(
        "csrf/",
        auth.csrf_token_view,
        name="csrf",
    ),
    path(
        "login/",
        auth.login_view,
        name="login",
    ),
    path(
        "me/",
        auth.me_view,
        name="me",
    ),
]