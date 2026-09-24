"""A per-address limit on contact submissions, to keep spam out of the inbox."""

from django.core.cache import cache
from django.utils.crypto import salted_hmac


CONTACT_MAX_SUBMISSIONS = 5
CONTACT_WINDOW_SECONDS = 60 * 60


def allow_contact_submission(ip_address):
    """Count a submission and report whether it is within the limit.

    Senders without a known address share one bucket, so a missing
    address cannot be used to skip the limit.
    """
    key = _cache_key(ip_address or "unknown")

    if cache.add(key, 1, timeout=CONTACT_WINDOW_SECONDS):
        return True

    try:
        count = cache.incr(key)
    except ValueError:
        # The entry expired between add() and incr(): start a new window.
        cache.set(key, 1, timeout=CONTACT_WINDOW_SECONDS)
        return True

    return count <= CONTACT_MAX_SUBMISSIONS


def _cache_key(ip_address):
    # Hashed so raw addresses are not written into the cache.
    digest = salted_hmac("nexcode:contact-throttle", ip_address).hexdigest()
    return f"nexcode:contact:{digest}"
