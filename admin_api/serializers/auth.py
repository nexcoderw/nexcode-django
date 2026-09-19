import json

from django.core.exceptions import ValidationError
from django.core.validators import validate_email


LOGIN_ERROR_INVALID_REQUEST = "invalid_request"
LOGIN_ERROR_INVALID_CREDENTIALS = "invalid_credentials"
LOGIN_ERROR_INVALID_REMEMBER_ME = "invalid_remember_me"


def parse_login_payload(raw_body):
    """Validate and normalize an admin login request body."""
    try:
        payload = json.loads(
            raw_body or b"{}"
        )
    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):
        return None, LOGIN_ERROR_INVALID_REQUEST

    if not isinstance(payload, dict):
        return None, LOGIN_ERROR_INVALID_REQUEST

    email = payload.get("email")
    password = payload.get("password")
    remember_me = payload.get(
        "remember_me",
        False,
    )

    if not isinstance(email, str):
        return None, LOGIN_ERROR_INVALID_CREDENTIALS

    if not isinstance(password, str):
        return None, LOGIN_ERROR_INVALID_CREDENTIALS

    if not isinstance(remember_me, bool):
        return None, LOGIN_ERROR_INVALID_REMEMBER_ME

    email = email.strip().lower()

    if not email or not password:
        return None, LOGIN_ERROR_INVALID_CREDENTIALS

    try:
        validate_email(email)
    except ValidationError:
        return None, LOGIN_ERROR_INVALID_CREDENTIALS

    return (
        {
            "email": email,
            "password": password,
            "remember_me": remember_me,
        },
        None,
    )


def serialize_admin(user):
    """Return the public admin account representation."""
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