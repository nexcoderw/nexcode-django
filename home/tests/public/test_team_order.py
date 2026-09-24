"""The public pages list team members in the order set in the admin."""

from django.test import TestCase, override_settings
from django.urls import reverse

from home.models import Team
from home.views import HOME_TEAM_PREVIEW_SIZE


@override_settings(
    SECURE_SSL_REDIRECT=False,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class PublicTeamOrderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Created out of order on purpose: the pages must sort, not echo
        # insertion order. Bea and Ann share a position, so name decides.
        for name, display_order in (
            ("Cara", 3),
            ("Bea", 1),
            ("Eve", 5),
            ("Ann", 1),
            ("Dan", 4),
        ):
            Team.objects.create(
                name=name,
                position="Engineer",
                display_order=display_order,
            )

    def names(self, response):
        return [member.name for member in response.context["team"]]

    def test_team_page_follows_display_order(self):
        response = self.client.get(reverse("base:team"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.names(response),
            ["Ann", "Bea", "Cara", "Dan", "Eve"],
        )

    def test_about_page_follows_display_order(self):
        response = self.client.get(reverse("base:about"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.names(response),
            ["Ann", "Bea", "Cara", "Dan", "Eve"],
        )

    def test_home_page_previews_the_first_members(self):
        response = self.client.get(reverse("base:home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.names(response),
            ["Ann", "Bea", "Cara", "Dan"][:HOME_TEAM_PREVIEW_SIZE],
        )

        # The section used to render "Coming Soon" because no members
        # reached the template; the members' names must now appear.
        self.assertContains(response, "Ann")
        self.assertNotContains(response, "Coming Soon")
