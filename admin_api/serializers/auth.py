import json

from django.core.exceptions import ValidationError
from django.core.validators import validate_email


LOGIN_ERROR_INVALID_REQUEST = "invalid_request"
LOGIN_ERROR_INVALID_CREDENTIALS = "invalid_credentials"
LOGIN_ERROR_INVALID_REMEMBER_ME = "invalid_remember_me"
PASSWORD_RESET_ERROR_INVALID_REQUEST = (
    "invalid_request"
)

PASSWORD_RESET_ERROR_PASSWORD_MISMATCH = (
    "password_mismatch"
)

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

def parse_password_reset_request_payload(
    raw_body,
):
    payload = _parse_json_object(
        raw_body
    )

    if payload is None:
        return (
            None,
            PASSWORD_RESET_ERROR_INVALID_REQUEST,
        )

    email = payload.get("email")

    if not isinstance(email, str):
        return (
            None,
            PASSWORD_RESET_ERROR_INVALID_REQUEST,
        )

    email = email.strip().lower()

    if not email:
        return (
            None,
            PASSWORD_RESET_ERROR_INVALID_REQUEST,
        )

    try:
        validate_email(email)
    except ValidationError:
        return (
            None,
            PASSWORD_RESET_ERROR_INVALID_REQUEST,
        )

    return (
        {
            "email": email,
        },
        None,
    )


def parse_password_reset_verify_payload(
    raw_body,
):
    payload = _parse_json_object(
        raw_body
    )

    if payload is None:
        return (
            None,
            PASSWORD_RESET_ERROR_INVALID_REQUEST,
        )

    challenge_id = payload.get(
        "challenge_id"
    )
    code = payload.get("code")

    if (
        not isinstance(
            challenge_id,
            str,
        )
        or not challenge_id
        or not isinstance(code, str)
        or len(code) != 6
        or not code.isdigit()
    ):
        return (
            None,
            PASSWORD_RESET_ERROR_INVALID_REQUEST,
        )

    return (
        {
            "challenge_id":
                challenge_id,
            "code": code,
        },
        None,
    )


def parse_password_reset_confirm_payload(
    raw_body,
):
    payload = _parse_json_object(
        raw_body
    )

    if payload is None:
        return (
            None,
            PASSWORD_RESET_ERROR_INVALID_REQUEST,
        )

    reset_token = payload.get(
        "reset_token"
    )
    password = payload.get(
        "password"
    )
    confirm_password = payload.get(
        "confirm_password"
    )

    if (
        not isinstance(
            reset_token,
            str,
        )
        or not reset_token
        or not isinstance(
            password,
            str,
        )
        or not password
        or not isinstance(
            confirm_password,
            str,
        )
        or not confirm_password
    ):
        return (
            None,
            PASSWORD_RESET_ERROR_INVALID_REQUEST,
        )

    if password != confirm_password:
        return (
            None,
            PASSWORD_RESET_ERROR_PASSWORD_MISMATCH,
        )

    return (
        {
            "reset_token":
                reset_token,
            "password":
                password,
        },
        None,
    )


def _parse_json_object(raw_body):
    try:
        payload = json.loads(
            raw_body or b"{}"
        )
    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):
        return None

    if not isinstance(
        payload,
        dict,
    ):
        return None

    return payload