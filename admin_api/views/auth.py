import uuid
import logging
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
from admin_api.security.login_throttle import (
    get_login_retry_after,
    record_login_failure,
    reset_login_throttle,
)
from django.core.exceptions import ValidationError

from admin_api.serializers.auth import (
    PASSWORD_RESET_ERROR_INVALID_REQUEST,
    PASSWORD_RESET_ERROR_PASSWORD_MISMATCH,
    parse_password_reset_confirm_payload,
    parse_password_reset_request_payload,
    parse_password_reset_verify_payload,
)
from admin_api.services.password_reset import (
    confirm_admin_password_reset,
    request_admin_password_reset,
    verify_admin_password_reset,
)

logger = logging.getLogger(
    __name__
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

    email = payload["email"]

    retry_after = get_login_retry_after(
        email
    )

    if retry_after is not None:
        return login_throttled_response(
            retry_after
        )

    user = authenticate(
        request=request,
        username=email,
        password=payload["password"],
    )

    if (
        user is None
        or not is_nexcode_admin(user)
    ):
        retry_after = record_login_failure(
            email
        )

        if retry_after is not None:
            return login_throttled_response(
                retry_after
            )

        return invalid_credentials_response()

    reset_login_throttle(email)

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


def login_throttled_response(retry_after):
    response = JsonResponse(
        {
            "status": "error",
            "message": (
                "Too many sign-in attempts. "
                "Please try again later."
            ),
        },
        status=429,
    )

    response["Retry-After"] = str(
        retry_after
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

def password_reset_request_view(
    request,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    payload, error = (
        parse_password_reset_request_payload(
            request.body
        )
    )

    if (
        error
        == PASSWORD_RESET_ERROR_INVALID_REQUEST
    ):
        return JsonResponse(
            {
                "status": "error",
                "message":
                    "Enter a valid email address.",
            },
            status=400,
        )

    try:
        challenge_id = (
            request_admin_password_reset(
                payload["email"]
            )
        )
    except Exception:
        logger.exception(
            "Administrator password reset "
            "email delivery failed."
        )

        # Preserve the same outward shape so
        # account existence is not exposed.
        challenge_id = str(
            uuid.uuid4()
        )

    response = JsonResponse(
        {
            "status": "success",
            "message": (
                "If an eligible administrator "
                "account exists, a verification "
                "code has been sent."
            ),
            "data": {
                "challenge_id":
                    challenge_id,
            },
        }
    )

    response["Cache-Control"] = (
        "no-store"
    )

    return response


def password_reset_verify_view(
    request,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    payload, error = (
        parse_password_reset_verify_payload(
            request.body
        )
    )

    if error is not None:
        return JsonResponse(
            {
                "status": "error",
                "message":
                    "Invalid verification request.",
            },
            status=400,
        )

    reset_token = (
        verify_admin_password_reset(
            payload["challenge_id"],
            payload["code"],
        )
    )

    if reset_token is None:
        return JsonResponse(
            {
                "status": "error",
                "message": (
                    "The verification code is "
                    "invalid or has expired."
                ),
            },
            status=400,
        )

    response = JsonResponse(
        {
            "status": "success",
            "message":
                "Verification successful.",
            "data": {
                "reset_token":
                    reset_token,
            },
        }
    )

    response["Cache-Control"] = (
        "no-store"
    )

    return response


def password_reset_confirm_view(
    request,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    payload, error = (
        parse_password_reset_confirm_payload(
            request.body
        )
    )

    if (
        error
        == PASSWORD_RESET_ERROR_PASSWORD_MISMATCH
    ):
        return JsonResponse(
            {
                "status": "error",
                "message":
                    "Passwords do not match.",
                "errors": {
                    "confirm_password": [
                        "Passwords do not match."
                    ],
                },
            },
            status=400,
        )

    if error is not None:
        return JsonResponse(
            {
                "status": "error",
                "message":
                    "Invalid password reset request.",
            },
            status=400,
        )

    try:
        success = (
            confirm_admin_password_reset(
                payload["reset_token"],
                payload["password"],
            )
        )
    except ValidationError as error:
        return JsonResponse(
            {
                "status": "error",
                "message": (
                    "Password does not meet "
                    "the security requirements."
                ),
                "errors": {
                    "password":
                        error.messages,
                },
            },
            status=400,
        )

    if not success:
        return JsonResponse(
            {
                "status": "error",
                "message": (
                    "The password reset session "
                    "is invalid or has expired."
                ),
            },
            status=400,
        )

    response = JsonResponse(
        {
            "status": "success",
            "message": (
                "Password reset successfully."
            ),
        }
    )

    response["Cache-Control"] = (
        "no-store"
    )

    return response