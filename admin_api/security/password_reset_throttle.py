from django.core.cache import cache
from django.utils.crypto import salted_hmac

from admin_api.constants import (
    NEXCODE_ADMIN_PASSWORD_RESET_REQUEST_COOLDOWN_SECONDS,
)


CACHE_KEY_PREFIX = "nexcode:admin-password-reset"


def allow_password_reset_request(email):
    """
    Return True once per cooldown period for a normalized email.
    """
    return cache.add(
        _request_key(email),
        True,
        timeout=(
            NEXCODE_ADMIN_PASSWORD_RESET_REQUEST_COOLDOWN_SECONDS
        ),
    )


def _request_key(email):
    normalized_email = (
        email.strip().lower()
    )

    digest = salted_hmac(
        "admin_api.password_reset_request",
        normalized_email,
        algorithm="sha256",
    ).hexdigest()

    return (
        f"{CACHE_KEY_PREFIX}:request:"
        f"{digest}"
    )