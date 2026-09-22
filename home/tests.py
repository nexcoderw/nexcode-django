"""Public page contracts for the remaining home features."""

import json
from html.parser import HTMLParser
from xml.etree import ElementTree

from django.test import TestCase, override_settings
from django.urls import reverse

from home.models import Contact, Team
from home.seo import PAGES, json_ld
from home.templatetags.content_tags import rich_text


class PageHTML(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def elements(self, tag):
        return [attrs for name, attrs in self.tags if name == tag]


@override_settings(
    SEARCH_ENGINE_INDEXING=True,
    SITE_URL="https://nexcode.africa",
    SECURE_SSL_REDIRECT=False,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class PublicPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member = Team.objects.create(
            name="Example Developer", position="Software developer"
        )

    def page_routes(self):
        return [reverse(f"base:{name}") for name in PAGES] + [
            reverse("base:getTeamMember", args=[self.member.slug])
        ]

    def test_public_pages_render_with_canonical_metadata(self):
        for url in self.page_routes():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                page = PageHTML(response.content.decode())
                self.assertGreaterEqual(len(page.elements("h1")), 1)
                self.assertEqual(page.elements("html")[0]["lang"], "en")
                self.assertEqual(
                    response.context["seo"]["canonical"],
                    "https://nexcode.africa" + url,
                )

    def test_retired_content_returns_gone(self):
        for path in (
            "/portfolio/",
            "/work/old-project",
            "/blogs/",
            "/blog/old-post/",
            "/testimony/",
            "/training/",
            "/training/old-course/",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 410)

    def test_sitemap_only_contains_live_pages(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        root = ElementTree.fromstring(response.content)
        urls = [element.text for element in root.findall("{*}url/{*}loc")]
        self.assertEqual(len(urls), len(set(urls)))
        self.assertIn(
            "https://nexcode.africa"
            + reverse("base:getTeamMember", args=[self.member.slug]),
            urls,
        )
        for url in urls:
            path = url.removeprefix("https://nexcode.africa")
            self.assertEqual(self.client.get(path).status_code, 200)

    def test_robots_and_preview_indexing(self):
        self.assertContains(
            self.client.get("/robots.txt"),
            "Sitemap: https://nexcode.africa/sitemap.xml",
        )
        with override_settings(SEARCH_ENGINE_INDEXING=False):
            response = self.client.get("/about/")
            self.assertEqual(response["X-Robots-Tag"], "noindex, follow")
            self.assertEqual(self.client.get("/sitemap.xml").status_code, 404)

    def test_contact_validates_and_saves(self):
        invalid = self.client.post(
            "/contact/",
            {
                "name": "Sample Client",
                "email": "invalid",
                "subject": "Website",
                "message": "Hello",
            },
        )
        self.assertContains(invalid, "Enter a valid email address.")
        self.assertEqual(Contact.objects.count(), 0)
        valid = self.client.post(
            "/contact/",
            {
                "name": "Sample Client",
                "email": "client@example.com",
                "subject": "Website",
                "message": "Hello",
            },
        )
        self.assertRedirects(valid, "/contact/")
        self.assertEqual(Contact.objects.count(), 1)

    def test_service_enquiry_prefills_subject(self):
        response = self.client.get("/contact/?service=Mobile%20app%20development")
        self.assertEqual(
            response.context["form"]["subject"].value(), "Mobile app development"
        )

    def test_json_ld_escapes_script_delimiters(self):
        value = {"headline": '</script><script>alert("test")</script>'}
        encoded = json_ld(value)
        self.assertNotIn("<", encoded)
        self.assertEqual(json.loads(encoded), value)

    def test_rich_text_removes_unsafe_markup(self):
        content = rich_text(
            '<h1>Heading</h1><p onclick="bad()">Text <strong>bold</strong></p><a href="javascript:bad()">link</a><script>bad()</script>'
        )
        self.assertIn("<strong>bold</strong>", content)
        for unsafe in ("<h1", "<script", "onclick", "javascript:"):
            self.assertNotIn(unsafe, content)
