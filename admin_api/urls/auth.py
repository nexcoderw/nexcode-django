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
    path(
        "logout/",
        auth.logout_view,
        name="logout",
    ),
    path(
        "password-reset/request/",
        auth.password_reset_request_view,
        name="password-reset-request",
    ),
    path(
        "password-reset/verify/",
        auth.password_reset_verify_view,
        name="password-reset-verify",
    ),
    path(
        "password-reset/confirm/",
        auth.password_reset_confirm_view,
        name="password-reset-confirm",
    ),
]