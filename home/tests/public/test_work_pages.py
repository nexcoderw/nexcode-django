"""The public portfolio: only published work reaches the site."""

from xml.etree import ElementTree

from django.test import TestCase, override_settings
from django.urls import reverse

from home.models import Portfolio, PortfolioRepository
from home.views import HOME_WORK_PREVIEW_SIZE


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
class PublicWorkTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.published = Portfolio.objects.create(
            name="Published Project",
            summary="A shipped client platform.",
            description="<p>Built <strong>end to end</strong>.</p><script>bad()</script>",
            category=Portfolio.Category.WEB_APPLICATION,
            project_type=Portfolio.ProjectType.CLIENT_PROJECT,
            status=Portfolio.Status.PUBLISHED,
        )
        PortfolioRepository.objects.create(
            portfolio=cls.published,
            label="Source on GitHub",
            url="https://github.com/nexcoderw/example",
        )

        cls.draft = Portfolio.objects.create(
            name="Draft Project",
            category=Portfolio.Category.BRANDING,
            project_type=Portfolio.ProjectType.CLIENT_PROJECT,
            status=Portfolio.Status.DRAFT,
        )

        cls.archived = Portfolio.objects.create(
            name="Archived Project",
            category=Portfolio.Category.UI_UX,
            project_type=Portfolio.ProjectType.CLIENT_PROJECT,
            status=Portfolio.Status.ARCHIVED,
        )

    def test_portfolio_lists_only_published_work(self):
        response = self.client.get(reverse("base:portfolio"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["portfolio"]), [self.published])
        self.assertContains(response, "Web Application")
        self.assertNotContains(response, "Draft Project")
        self.assertNotContains(response, "Archived Project")

    def test_home_previews_published_work_through_the_component(self):
        response = self.client.get(reverse("base:home"))

        self.assertTemplateUsed(response, "inc/project-list.html")
        self.assertEqual(list(response.context["portfolio"]), [self.published])
        self.assertContains(
            response, reverse("base:workDetails", args=[self.published.slug])
        )
        self.assertNotContains(response, "Draft Project")

    def test_home_preview_is_capped(self):
        for number in range(HOME_WORK_PREVIEW_SIZE + 2):
            Portfolio.objects.create(
                name=f"Extra {number}",
                category=Portfolio.Category.WEB_APPLICATION,
                project_type=Portfolio.ProjectType.CLIENT_PROJECT,
                status=Portfolio.Status.PUBLISHED,
            )

        response = self.client.get(reverse("base:home"))

        self.assertEqual(len(response.context["portfolio"]), HOME_WORK_PREVIEW_SIZE)

    def test_details_render_published_work(self):
        response = self.client.get(
            reverse("base:workDetails", args=[self.published.slug])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["seo"]["title"],
            "Published Project — Project | NEXCODE Africa",
        )
        self.assertEqual(
            response.context["seo"]["description"], "A shipped client platform."
        )
        self.assertContains(response, "<strong>end to end</strong>", html=True)
        self.assertNotContains(response, "<script>bad()")
        # With no live URL, the header links to the repository instead.
        self.assertContains(response, "https://github.com/nexcoderw/example")
        self.assertContains(response, "Client Project")

    def test_details_hide_unpublished_work(self):
        for work in (self.draft, self.archived):
            with self.subTest(status=work.status):
                response = self.client.get(
                    reverse("base:workDetails", args=[work.slug])
                )
                self.assertEqual(response.status_code, 404)

    def test_sitemap_lists_only_published_work(self):
        response = self.client.get("/sitemap.xml")
        root = ElementTree.fromstring(response.content)
        urls = [element.text for element in root.findall("{*}url/{*}loc")]

        self.assertIn("https://nexcode.africa/portfolio/", urls)
        self.assertIn(f"https://nexcode.africa/work/{self.published.slug}", urls)
        self.assertNotIn(f"https://nexcode.africa/work/{self.draft.slug}", urls)
        self.assertNotIn(f"https://nexcode.africa/work/{self.archived.slug}", urls)
