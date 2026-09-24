"""Metadata and rendering for public pages, using a trusted canonical origin."""

import json
from html import unescape
from urllib.parse import urljoin, urlsplit

from django.conf import settings
from django.shortcuts import render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import Truncator

PAGES = {
    "home": (
        "Software Development in Kigali, Rwanda",
        "NEXCODE builds websites, mobile apps and business systems from Kigali, Rwanda. Explore custom development, ready-to-use platforms and ongoing support.",
    ),
    "about": (
        "About Our Kigali Technology Studio",
        "Meet NEXCODE, a technology studio founded in 2019 at Norrsken House Kigali. Learn how we approach custom products and ready-to-use business systems.",
    ),
    "services": (
        "Software, Design and Technology Services",
        "Explore NEXCODE services: custom software, mobile apps, UI/UX design, networking, digital marketing and maintenance. Find the right support for your business.",
    ),
    "portfolio": (
        "Our Work and Recent Projects",
        "Explore NEXCODE projects: web applications, mobile apps, UI/UX design and branding built for businesses from our studio in Kigali.",
    ),
    "team": (
        "Meet the NEXCODE Team",
        "Meet the people behind NEXCODE. Explore team roles and professional profiles from our technology studio in Kigali.",
    ),
    "contact": (
        "Contact NEXCODE in Kigali",
        "Discuss a software project, an existing system or technical support with NEXCODE. Find our email and phone contact details in Kigali.",
    ),
}


def plain_text(value, limit=160):
    """Make a short, whitespace-normalized excerpt; template escaping stays enabled."""
    text = " ".join(unescape(strip_tags(value or "")).split())
    return Truncator(text).chars(limit)


def absolute_url(path):
    return urljoin(settings.SITE_URL + "/", path)


def json_ld(value):
    # JSON script elements are raw text: escape HTML delimiters before marking safe.
    return (
        json.dumps(value, ensure_ascii=True)
        .replace("<", "\\u003C")
        .replace(">", "\\u003E")
        .replace("&", "\\u0026")
    )


def render_page(
    request,
    template,
    context=None,
    *,
    title=None,
    description=None,
    image=None,
):
    context = dict(context or {})
    route = request.resolver_match.url_name
    default_title, default_description = PAGES.get(
        route, ("NEXCODE Africa", "Technology built around your business.")
    )
    page_title = title or default_title
    page_description = plain_text(description or default_description)
    canonical = absolute_url(
        reverse(request.resolver_match.view_name, kwargs=request.resolver_match.kwargs)
    )
    page = context.get("page_obj")
    if page is not None and page.number > 1:
        canonical += f"?page={page.number}"
        page_title += f" — Page {page.number}"
        page_description = plain_text(f"Page {page.number}. {page_description}")
    page_title += " | NEXCODE Africa"
    image_url = absolute_url(image or static("img/logo-w.png"))
    if urlsplit(image_url).scheme not in {"http", "https"}:
        image_url = absolute_url(static("img/logo-w.png"))
    indexable = settings.SEARCH_ENGINE_INDEXING
    organization = {
        "@type": "Organization",
        "@id": settings.SITE_URL + "/#organization",
        "name": "NEXCODE Africa",
        "url": settings.SITE_URL + "/",
        "logo": absolute_url(static("img/logo-w.png")),
        "sameAs": ["https://www.linkedin.com/company/nexcode-africa/"],
    }
    graph = [organization]
    context.update(
        {
            "seo": {
                "title": page_title,
                "description": page_description,
                "canonical": canonical,
                "image": image_url,
                "type": "website",
                "robots": "index, follow" if indexable else "noindex, follow",
                "structured_data": json_ld(
                    {"@context": "https://schema.org", "@graph": graph}
                ),
            },
        }
    )
    response = render(request, template, context)
    if not indexable:
        response["X-Robots-Tag"] = "noindex, follow"
    return response
