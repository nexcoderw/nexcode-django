"""Team members on the public pages: no detail pages, and only real links."""

from django.test import TestCase, override_settings
from django.urls import reverse

from home.models import Team


@override_settings(
    SECURE_SSL_REDIRECT=False,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class PublicTeamProfileTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.both = Team.objects.create(
            name="Both Profiles",
            position="Engineer",
            linkedin="https://www.linkedin.com/in/both",
            github="https://github.com/both",
            display_order=1,
        )

        cls.linkedin_only = Team.objects.create(
            name="LinkedIn Only",
            position="Engineer",
            linkedin="https://www.linkedin.com/in/linkedin-only",
            display_order=2,
        )

        cls.neither = Team.objects.create(
            name="No Profiles",
            position="Engineer",
            display_order=3,
        )

    def test_retired_detail_page_redirects_to_the_team_page(self):
        response = self.client.get(f"/team/{self.both.slug}/")

        self.assertRedirects(
            response,
            reverse("base:team"),
            status_code=301,
            fetch_redirect_response=False,
        )

    def test_unknown_member_url_also_redirects(self):
        # Old links for members since deleted land on the team page too.
        response = self.client.get("/team/no-longer-here/")

        self.assertEqual(response.status_code, 301)

    def test_pages_render_only_the_links_a_member_has(self):
        # Keyed on the member links' own labels: the footer and mobile
        # menu use the same icon classes for NEXCODE's accounts.
        for route in ("base:team", "base:about", "base:home"):
            with self.subTest(route=route):
                html = self.client.get(reverse(route)).content.decode()

                self.assertIn("Both Profiles on LinkedIn", html)
                self.assertIn("Both Profiles on GitHub", html)
                self.assertIn("LinkedIn Only on LinkedIn", html)

                # Missing profiles leave no icon behind.
                self.assertNotIn("LinkedIn Only on GitHub", html)
                self.assertNotIn("No Profiles on LinkedIn", html)
                self.assertNotIn("No Profiles on GitHub", html)

    def test_member_names_no_longer_link_anywhere(self):
        html = self.client.get(reverse("base:team")).content.decode()

        self.assertNotIn(f"/team/{self.both.slug}/", html)
