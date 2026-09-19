from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.http import JsonResponse
from django.middleware.csrf import get_token

from admin_api.constants import (
    NEXCODE_ADMIN_REMEMBER_SESSION_SECONDS,
)
from admin_api.permissions import (
    is_nexcode_admin,
    nexcode_admin_required,
)
from admin_api.serializers.auth import (
    LOGIN_ERROR_INVALID_CREDENTIALS,
    LOGIN_ERROR_INVALID_REMEMBER_ME,
    LOGIN_ERROR_INVALID_REQUEST,
    parse_login_payload,
    serialize_admin,
)


def csrf_token_view(request):
    if request.method != "GET":
        return method_not_allowed(["GET"])

    response = JsonResponse(
        {
            "status": "success",
            "data": {
                "csrf_token": get_token(request),
            },
        }
    )

    response["Cache-Control"] = "no-store"

    return response


def login_view(request):
    if request.method != "POST":
        return method_not_allowed(["POST"])

    payload, error = parse_login_payload(
        request.body
    )

    if error == LOGIN_ERROR_INVALID_REQUEST:
        return JsonResponse(
            {
                "status": "error",
                "message": "Invalid request body.",
            },
            status=400,
        )

    if error == LOGIN_ERROR_INVALID_REMEMBER_ME:
        return JsonResponse(
            {
                "status": "error",
                "message": (
                    "remember_me must be a boolean."
                ),
            },
            status=400,
        )

    if error == LOGIN_ERROR_INVALID_CREDENTIALS:
        return invalid_credentials_response()

    user = authenticate(
        request=request,
        username=payload["email"],
        password=payload["password"],
    )

    if user is None:
        return invalid_credentials_response()

    if not is_nexcode_admin(user):
        return invalid_credentials_response()

    django_login(
        request,
        user,
    )

    if payload["remember_me"]:
        request.session.set_expiry(
            NEXCODE_ADMIN_REMEMBER_SESSION_SECONDS
        )
    else:
        request.session.set_expiry(0)

    response = JsonResponse(
        {
            "status": "success",
            "message": "Signed in successfully.",
            "data": {
                "admin": serialize_admin(user),
            },
        }
    )

    response["Cache-Control"] = "no-store"

    return response


@nexcode_admin_required
def me_view(request):
    if request.method != "GET":
        return method_not_allowed(["GET"])

    response = JsonResponse(
        {
            "status": "success",
            "data": {
                "admin": serialize_admin(
                    request.user
                ),
            },
        }
    )

    response["Cache-Control"] = "no-store"

    return response

def logout_view(request):
    if request.method != "POST":
        return method_not_allowed(["POST"])

    django_logout(request)

    response = JsonResponse(
        {
            "status": "success",
            "message": "Signed out successfully.",
        }
    )

    response["Cache-Control"] = "no-store"

    return response


def invalid_credentials_response():
    response = JsonResponse(
        {
            "status": "error",
            "message": (
                "Invalid email or password."
            ),
        },
        status=401,
    )

    response["Cache-Control"] = "no-store"

    return response


def method_not_allowed(allowed_methods):
    response = JsonResponse(
        {
            "status": "error",
            "message": "Method not allowed.",
        },
        status=405,
    )

    response["Allow"] = ", ".join(
        allowed_methods
    )

    return response