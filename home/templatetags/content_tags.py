"""Safe presentation of editor-managed rich text and external links."""

from urllib.parse import urlsplit

import nh3
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Exclude h1 so article content cannot create another primary page heading.
RICH_TEXT = nh3.Cleaner(
    tags={
        "p",
        "br",
        "strong",
        "b",
        "em",
        "i",
        "u",
        "s",
        "ul",
        "ol",
        "li",
        "h2",
        "h3",
        "h4",
        "blockquote",
        "a",
        "img",
        "pre",
        "code",
        "table",
        "thead",
        "tbody",
        "tr",
        "th",
        "td",
    },
    attributes={
        "a": {"href", "title"},
        "img": {"src", "alt", "width", "height"},
        "th": {"scope", "colspan", "rowspan"},
        "td": {"colspan", "rowspan"},
    },
    url_schemes={"https", "http", "mailto"},
)


@register.filter
def rich_text(value):
    """Preserve supported formatting while removing executable HTML."""
    return mark_safe(RICH_TEXT.clean(value or ""))


@register.filter
def public_url(value):
    try:
        parsed = urlsplit(value or "")
    except ValueError:
        return ""
    return value if parsed.scheme in {"https", "http"} and parsed.netloc else ""
