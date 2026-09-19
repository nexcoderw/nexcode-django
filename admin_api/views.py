import json

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.middleware.csrf import get_token

from admin_api.constants import (
    NEXCODE_ADMIN_REMEMBER_SESSION_SECONDS,
)
from admin_api.permissions import is_nexcode_admin


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

    payload = parse_json_request(request)

    if payload is None:
        return JsonResponse(
            {
                "status": "error",
                "message": "Invalid request body.",
            },
            status=400,
        )

    email = payload.get("email")
    password = payload.get("password")
    remember_me = payload.get(
        "remember_me",
        False,
    )

    if not isinstance(email, str):
        return invalid_credentials_response()

    if not isinstance(password, str):
        return invalid_credentials_response()

    if not isinstance(remember_me, bool):
        return JsonResponse(
            {
                "status": "error",
                "message": (
                    "remember_me must be a boolean."
                ),
            },
            status=400,
        )

    email = email.strip().lower()

    if not email or not password:
        return invalid_credentials_response()

    try:
        validate_email(email)
    except ValidationError:
        return invalid_credentials_response()

    user = authenticate(
        request=request,
        username=email,
        password=password,
    )

    if user is None:
        return invalid_credentials_response()

    if not is_nexcode_admin(user):
        return invalid_credentials_response()

    django_login(
        request,
        user,
    )

    if remember_me:
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


def serialize_admin(user):
    return {
        "id": user.pk,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": (
            user.get_full_name().strip()
            or user.email
        ),
    }


def parse_json_request(request):
    try:
        payload = json.loads(
            request.body or b"{}"
        )
    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):
        return None

    if not isinstance(payload, dict):
        return None

    return payload


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