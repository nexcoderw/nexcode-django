"""Public page contracts: metadata, publication boundaries and usable enquiries."""

import json
from datetime import date, timedelta
from html.parser import HTMLParser
from xml.etree import ElementTree

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from home.models import Blog, Contact, Portfolio, PortfolioImage, Team, Training
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
        cls.author = get_user_model().objects.create_user(
            username="editor", first_name="Studio", last_name="Editor"
        )
        cls.member = Team.objects.create(
            name="Example Developer", position="Software developer"
        )
        cls.work = Portfolio.objects.create(
            name="Booking platform",
            publish=True,
            project_category="Client Project",
            description="<p>A booking workflow.</p>",
        )
        cls.work.team_members.add(cls.member)
        cls.hidden_work = Portfolio.objects.create(
            name="Private project", publish=False
        )
        cls.blog = Blog.objects.create(
            title="Building useful software",
            status="Published",
            author=cls.author,
            excerpt="A practical development guide.",
            content='<p>A useful article.</p><script>alert("bad")</script>',
        )
        cls.draft = Blog.objects.create(title="Private draft", status="Draft")
        cls.scheduled = Blog.objects.create(
            title="Future article",
            status="Published",
            published_at=timezone.now() + timedelta(days=3),
        )
        cls.training = Training.objects.create(
            title="Software workshop",
            description="<p>A practical workshop.</p>",
            price=10000,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
        )

    def page_routes(self):
        routes = [reverse(f"base:{name}") for name in PAGES]
        routes += [
            reverse(f"base:{name}", args=[item.slug])
            for name, item in (
                ("workDetails", self.work),
                ("getTeamMember", self.member),
                ("getBlogDetails", self.blog),
                ("trainingDetail", self.training),
            )
        ]
        return routes

    def test_every_public_page_has_unique_metadata_and_one_heading(self):
        titles, descriptions = set(), set()
        for url in self.page_routes():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                page = PageHTML(response.content.decode())
                self.assertEqual(len(page.elements("h1")), 1)
                self.assertEqual(len(page.elements("title")), 1)
                self.assertEqual(page.elements("html")[0]["lang"], "en")
                metadata = response.context["seo"]
                self.assertNotIn(metadata["title"], titles)
                self.assertNotIn(metadata["description"], descriptions)
                titles.add(metadata["title"])
                descriptions.add(metadata["description"])
                canonical = [
                    link["href"]
                    for link in page.elements("link")
                    if link.get("rel") == "canonical"
                ]
                self.assertEqual(canonical, ["https://nexcode.africa" + url])
                description = [
                    meta
                    for meta in page.elements("meta")
                    if meta.get("name") == "description"
                ]
                self.assertEqual(len(description), 1)
                graph = json.loads(metadata["structured_data"])
                self.assertEqual(graph["@graph"][0]["name"], "NEXCODE Africa")
                for link in page.elements("a"):
                    self.assertNotIn(link.get("href"), ("", "#", "#0"))

    def test_canonicals_ignore_incoming_host_and_tracking(self):
        with override_settings(ALLOWED_HOSTS=["preview.example"]):
            response = self.client.get(
                "/about/?utm_source=campaign", HTTP_HOST="preview.example"
            )
        self.assertEqual(
            response.context["seo"]["canonical"], "https://nexcode.africa/about/"
        )

    def test_unpublished_and_scheduled_content_is_not_public(self):
        for route, item in (
            ("workDetails", self.hidden_work),
            ("getBlogDetails", self.draft),
            ("getBlogDetails", self.scheduled),
        ):
            self.assertEqual(
                self.client.get(reverse(f"base:{route}", args=[item.slug])).status_code,
                404,
            )
        blogs = self.client.get(reverse("base:blogs"))
        self.assertContains(blogs, self.blog.title)
        self.assertNotContains(blogs, self.draft.title)
        self.assertNotContains(blogs, self.scheduled.title)
        self.hidden_work.team_members.add(self.member)
        self.assertNotContains(
            self.client.get(reverse("base:getTeamMember", args=[self.member.slug])),
            self.hidden_work.name,
        )

    def test_sitemap_contains_only_public_canonical_pages(self):
        response = self.client.get("/sitemap.xml", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        root = ElementTree.fromstring(response.content)
        urls = [element.text for element in root.findall("{*}url/{*}loc")]
        self.assertEqual(len(urls), len(set(urls)))
        self.assertTrue(all(url.startswith("https://nexcode.africa/") for url in urls))
        self.assertIn(
            "https://nexcode.africa"
            + reverse("base:workDetails", args=[self.work.slug]),
            urls,
        )
        self.assertNotContains(response, self.hidden_work.slug)
        self.assertNotContains(response, self.draft.slug)
        self.assertNotContains(response, self.scheduled.slug)
        self.assertNotIn("https://nexcode.africa/testimony/", urls)
        for url in urls:
            self.assertEqual(
                self.client.get(url.removeprefix("https://nexcode.africa")).status_code,
                200,
            )

    def test_robots_and_preview_indexing(self):
        self.assertContains(
            self.client.get("/robots.txt"),
            "Sitemap: https://nexcode.africa/sitemap.xml",
        )
        with override_settings(SEARCH_ENGINE_INDEXING=False):
            response = self.client.get("/about/")
            self.assertEqual(response["X-Robots-Tag"], "noindex, follow")
            self.assertContains(response, 'name="robots" content="noindex, follow"')
            self.assertNotContains(self.client.get("/robots.txt"), "Sitemap:")
            self.assertEqual(self.client.get("/sitemap.xml").status_code, 404)
        self.assertEqual(
            self.client.get("/testimony/")["X-Robots-Tag"], "noindex, follow"
        )

    def test_paginated_lists_have_distinct_canonical_urls(self):
        Blog.objects.bulk_create(
            [
                Blog(
                    title=f"Article {number}",
                    slug=f"article-{number}",
                    status="Published",
                    published_at=timezone.now(),
                )
                for number in range(13)
            ]
        )
        second = self.client.get("/blogs/?page=2&utm_source=test")
        self.assertEqual(
            second.context["seo"]["canonical"], "https://nexcode.africa/blogs/?page=2"
        )
        self.assertIn("Page 2", second.context["seo"]["title"])
        previous_links = [
            link["href"]
            for link in PageHTML(second.content.decode()).elements("a")
            if link.get("rel") == "prev"
        ]
        self.assertEqual(previous_links, ["/blogs/"])
        self.assertEqual(
            self.client.get("/blogs/?page=1").context["seo"]["canonical"],
            "https://nexcode.africa/blogs/",
        )
        for page in ("0", "-1", "invalid", "999"):
            self.assertEqual(self.client.get(f"/blogs/?page={page}").status_code, 404)

    def test_optional_images_and_empty_lists_render(self):
        for url in self.page_routes():
            self.assertEqual(self.client.get(url).status_code, 200)
        Blog.objects.all().delete()
        Portfolio.objects.all().delete()
        Team.objects.all().delete()
        Training.objects.all().delete()
        for name in ("home", "portfolio", "blogs", "team", "getTraining"):
            self.assertEqual(self.client.get(reverse(f"base:{name}")).status_code, 200)

    def test_article_dates_and_content_are_server_rendered_safely(self):
        response = self.client.get(
            reverse("base:getBlogDetails", args=[self.blog.slug])
        )
        self.assertContains(response, "A useful article.")
        self.assertContains(response, "Studio Editor")
        self.assertNotContains(response, '<script>alert("bad")</script>')
        self.assertNotContains(response, "Loading...")
        self.assertNotContains(response, "Post Comment")
        graph = json.loads(response.context["seo"]["structured_data"])
        article = graph["@graph"][1]
        self.assertEqual(article["@type"], "BlogPosting")
        self.assertEqual(article["author"]["name"], "Studio Editor")
        self.assertEqual(article["datePublished"], self.blog.published_at.isoformat())

    def test_json_ld_cannot_close_its_script_element(self):
        value = {"headline": '</script><script>alert("test")</script>'}
        encoded = json_ld(value)
        self.assertNotIn("<", encoded)
        self.assertEqual(json.loads(encoded), value)

    def test_rich_text_removes_scripts_handlers_and_unsafe_links(self):
        content = rich_text(
            '<h1>Heading</h1><p onclick="bad()">Text <strong>bold</strong></p><a href="javascript:bad()">link</a><img src="/image.jpg" onerror="bad()"><script>bad()</script>'
        )
        self.assertIn("<strong>bold</strong>", content)
        for unsafe in ("<h1", "<script", "onclick", "onerror", "javascript:"):
            self.assertNotIn(unsafe, content)

    def test_contact_validates_and_preserves_invalid_entries(self):
        response = self.client.post(
            "/contact/",
            {
                "name": "Sample Client",
                "email": "invalid",
                "subject": "New website",
                "message": "A project enquiry",
            },
        )
        self.assertContains(response, "Sample Client")
        self.assertContains(response, "Enter a valid email address.")
        self.assertContains(response, 'for="id_email"')
        self.assertEqual(Contact.objects.count(), 0)
        self.assertTrue(self.client.post("/contact/", {}).context["form"].errors)
        response = self.client.post(
            "/contact/",
            {
                "name": "Sample Client",
                "email": "client@example.com",
                "subject": "New website",
                "message": "A project enquiry",
            },
        )
        self.assertRedirects(response, "/contact/")
        self.assertEqual(Contact.objects.count(), 1)

    def test_service_enquiry_prefills_subject(self):
        response = self.client.get("/contact/?service=Mobile%20app%20development")
        self.assertEqual(
            response.context["form"]["subject"].value(), "Mobile app development"
        )

    def test_feedback_form_is_bound_on_empty_post(self):
        response = self.client.post("/testimony/", {})
        self.assertTrue(response.context["form"].errors)

    def test_project_list_queries_do_not_grow_per_card(self):
        PortfolioImage.objects.bulk_create(
            [PortfolioImage(portfolio=self.work, image="example.jpg")]
        )
        with CaptureQueriesContext(connection) as first:
            self.client.get("/portfolio/")
        for number in range(10):
            work = Portfolio.objects.create(
                name=f"Example {number}",
                publish=True,
                project_category="Client Project",
            )
            PortfolioImage.objects.bulk_create(
                [PortfolioImage(portfolio=work, image="example.jpg")]
            )
        with CaptureQueriesContext(connection) as many:
            self.client.get("/portfolio/")
        self.assertEqual(len(first), len(many))
        self.assertLessEqual(len(many), 4)

    def test_invalid_external_urls_do_not_render_empty_links(self):
        self.work.link = "javascript:alert(1)"
        self.work.repo_link = "invalid"
        self.work.save()
        self.member.linkedin = "javascript:alert(1)"
        self.member.save()
        for route, item in (("workDetails", self.work), ("getTeamMember", self.member)):
            response = self.client.get(reverse(f"base:{route}", args=[item.slug]))
            self.assertNotContains(response, 'href=""')
            self.assertNotContains(response, 'href="javascript:')
