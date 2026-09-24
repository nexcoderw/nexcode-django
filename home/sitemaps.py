"""The public sitemap: the site's canonical pages, on the canonical host."""

from types import SimpleNamespace
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.http import Http404
from django.urls import reverse
from django.views.decorators.http import require_safe

from home.seo import PAGES


class CanonicalSitemap(Sitemap):
    protocol = "https"

    def get_urls(self, page=1, site=None, protocol=None):
        # The canonical host is configuration, not a visitor-controlled request host.
        site = SimpleNamespace(domain=urlsplit(settings.SITE_URL).netloc)
        return super().get_urls(page=page, site=site, protocol="https")


class StaticSitemap(CanonicalSitemap):
    def items(self):
        return list(PAGES)

    def location(self, item):
        return reverse(f"base:{item}")



@require_safe
def public_sitemap(request):
    if not settings.SEARCH_ENGINE_INDEXING:
        raise Http404("The sitemap is only available on the public website.")
    return sitemap(
        request,
        sitemaps={
            "pages": StaticSitemap(),
        },
    )
