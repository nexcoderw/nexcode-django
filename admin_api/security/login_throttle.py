import math
import time

from django.core.cache import cache
from django.utils.crypto import salted_hmac

from admin_api.constants import (
    NEXCODE_ADMIN_LOGIN_MAX_FAILURES,
    NEXCODE_ADMIN_LOGIN_WINDOW_SECONDS,
)


CACHE_KEY_PREFIX = "nexcode:admin-login"


def get_login_retry_after(email):
    """
    Return the number of seconds until another login attempt is allowed.

    Returns None when the identifier is not currently blocked.
    """
    blocked_until = cache.get(
        _blocked_key(email)
    )

    if blocked_until is None:
        return None

    retry_after = math.ceil(
        blocked_until - time.time()
    )

    if retry_after <= 0:
        reset_login_throttle(email)
        return None

    return retry_after


def record_login_failure(email):
    """
    Record a failed authentication attempt.

    Returns the retry-after duration when the identifier becomes blocked.
    Otherwise returns None.
    """
    count_key = _failure_count_key(email)

    created = cache.add(
        count_key,
        1,
        timeout=NEXCODE_ADMIN_LOGIN_WINDOW_SECONDS,
    )

    if created:
        failure_count = 1
    else:
        try:
            failure_count = cache.incr(
                count_key
            )
        except ValueError:
            cache.set(
                count_key,
                1,
                timeout=(
                    NEXCODE_ADMIN_LOGIN_WINDOW_SECONDS
                ),
            )
            failure_count = 1

    if (
        failure_count
        < NEXCODE_ADMIN_LOGIN_MAX_FAILURES
    ):
        return None

    blocked_until = (
        time.time()
        + NEXCODE_ADMIN_LOGIN_WINDOW_SECONDS
    )

    cache.set(
        _blocked_key(email),
        blocked_until,
        timeout=NEXCODE_ADMIN_LOGIN_WINDOW_SECONDS,
    )

    return NEXCODE_ADMIN_LOGIN_WINDOW_SECONDS


def reset_login_throttle(email):
    """Remove login throttling state for an identifier."""
    cache.delete_many(
        [
            _failure_count_key(email),
            _blocked_key(email),
        ]
    )


def _failure_count_key(email):
    return (
        f"{CACHE_KEY_PREFIX}:failures:"
        f"{_identifier_digest(email)}"
    )


def _blocked_key(email):
    return (
        f"{CACHE_KEY_PREFIX}:blocked:"
        f"{_identifier_digest(email)}"
    )


def _identifier_digest(email):
    """
    Produce a keyed digest so raw email addresses are never placed
    in cache keys.
    """
    normalized_email = (
        email.strip().lower()
    )

    return salted_hmac(
        "admin_api.login_throttle",
        normalized_email,
        algorithm="sha256",
    ).hexdigest()