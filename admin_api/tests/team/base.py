import tempfile

from django.contrib.auth import (
    get_user_model,
)
from django.contrib.auth.models import (
    Group,
)
from django.test import (
    Client,
    TestCase,
    override_settings,
)
from django.test.client import (
    BOUNDARY,
    MULTIPART_CONTENT,
    encode_multipart,
)
from django.urls import reverse

from admin_api.constants import (
    NEXCODE_ADMIN_GROUP_NAME,
)


class TeamApiTestCase(TestCase):
    password = (
        "TestPassword123!"
    )

    def setUp(self):
        self.media_directory = (
            tempfile.TemporaryDirectory()
        )

        self.media_override = (
            override_settings(
                MEDIA_ROOT=(
                    self.media_directory
                    .name
                )
            )
        )

        self.media_override.enable()

        User = get_user_model()

        group, _ = (
            Group.objects.get_or_create(
                name=(
                    NEXCODE_ADMIN_GROUP_NAME
                )
            )
        )

        self.admin_user = (
            User.objects.create_user(
                username=(
                    "admin@nexcode.africa"
                ),
                email=(
                    "admin@nexcode.africa"
                ),
                password=self.password,
            )
        )

        self.admin_user.groups.add(
            group
        )

        self.regular_user = (
            User.objects.create_user(
                username=(
                    "user@nexcode.africa"
                ),
                email=(
                    "user@nexcode.africa"
                ),
                password=self.password,
            )
        )

        self.client = Client(
            enforce_csrf_checks=True,
        )

        self.csrf_url = reverse(
            "admin_api:auth:csrf"
        )

        self.list_url = reverse(
            "admin_api:team:list"
        )

        self.add_url = reverse(
            "admin_api:team:add"
        )

    def tearDown(self):
        self.media_override.disable()

        self.media_directory.cleanup()

    def login_admin(self):
        self.client.force_login(
            self.admin_user
        )

    def csrf_token(self):
        response = self.client.get(
            self.csrf_url
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        return response.json()[
            "data"
        ]["csrf_token"]

    def csrf_headers(self):
        return {
            "HTTP_X_CSRFTOKEN":
                self.csrf_token(),
        }

    def detail_url(
        self,
        team_member,
    ):
        return reverse(
            "admin_api:team:detail",
            kwargs={
                "team_id":
                    team_member.pk,
            },
        )

    def update_url(
        self,
        team_member,
    ):
        return reverse(
            "admin_api:team:update",
            kwargs={
                "team_id":
                    team_member.pk,
            },
        )

    def delete_url(
        self,
        team_member,
    ):
        return reverse(
            "admin_api:team:delete",
            kwargs={
                "team_id":
                    team_member.pk,
            },
        )

    def patch_multipart(
        self,
        url,
        data,
    ):
        body = encode_multipart(
            BOUNDARY,
            data,
        )

        return self.client.patch(
            url,
            data=body,
            content_type=(
                MULTIPART_CONTENT
            ),
            **self.csrf_headers(),
        )