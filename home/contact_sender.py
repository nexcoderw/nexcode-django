"""Who sent a contact message: the network address and the device used."""

import ipaddress
import re

from home.models import Contact


USER_AGENT_MAX_LENGTH = 512

# Checked in order: the first match wins, so more specific names come
# before the engines they are built on (Edge and Opera report Chrome,
# and Chrome reports Safari).
BROWSERS = (
    ("Edge", re.compile(r"Edg(?:e|A|iOS)?/")),
    ("Opera", re.compile(r"OPR/|Opera")),
    ("Samsung Internet", re.compile(r"SamsungBrowser/")),
    ("Firefox", re.compile(r"Firefox/|FxiOS/")),
    ("Chrome", re.compile(r"Chrome/|CriOS/")),
    ("Safari", re.compile(r"Safari/")),
)

OPERATING_SYSTEMS = (
    ("iPadOS", re.compile(r"iPad")),
    ("iOS", re.compile(r"iPhone|iPod")),
    ("Android", re.compile(r"Android")),
    ("Windows", re.compile(r"Windows")),
    ("macOS", re.compile(r"Macintosh|Mac OS X")),
    ("ChromeOS", re.compile(r"CrOS")),
    ("Linux", re.compile(r"Linux")),
)

BOT = re.compile(r"bot|crawl|spider|slurp|curl|wget|python-requests", re.I)
TABLET = re.compile(r"iPad|Tablet|Android(?!.*Mobile)", re.I)
MOBILE = re.compile(r"Mobi|iPhone|iPod|Android.*Mobile", re.I)


def client_ip(request):
    """The sender's address, or None when no valid one is present.

    In production nginx sets X-Real-IP to the connecting address and
    overwrites any value a visitor sends, so it is the trusted source.
    Without a proxy (local development) REMOTE_ADDR is the sender.
    """
    for candidate in (
        request.META.get("HTTP_X_REAL_IP", ""),
        request.META.get("REMOTE_ADDR", ""),
    ):
        try:
            return str(ipaddress.ip_address(candidate.strip()))
        except ValueError:
            continue

    return None


def describe_device(user_agent):
    """Device type, browser and operating system named by a user agent."""
    if not user_agent:
        return Contact.DeviceType.UNKNOWN, "", ""

    return (
        _device_type(user_agent),
        _first_match(BROWSERS, user_agent),
        _first_match(OPERATING_SYSTEMS, user_agent),
    )


def sender_details(request):
    """The Contact fields that record who sent a request."""
    user_agent = request.META.get("HTTP_USER_AGENT", "")[
        :USER_AGENT_MAX_LENGTH
    ]
    device_type, browser, operating_system = describe_device(user_agent)

    return {
        "ip_address": client_ip(request),
        "user_agent": user_agent,
        "device_type": device_type,
        "browser": browser,
        "operating_system": operating_system,
    }


def _device_type(user_agent):
    if BOT.search(user_agent):
        return Contact.DeviceType.BOT

    if TABLET.search(user_agent):
        return Contact.DeviceType.TABLET

    if MOBILE.search(user_agent):
        return Contact.DeviceType.MOBILE

    return Contact.DeviceType.DESKTOP


def _first_match(patterns, user_agent):
    return next(
        (name for name, pattern in patterns if pattern.search(user_agent)),
        "",
    )
