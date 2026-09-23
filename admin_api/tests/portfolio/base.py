import json
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
from home.models import Portfolio


class PortfolioApiTestCase(
    TestCase
):
    """Shared fixtures for the portfolio administration endpoints.

    Uploads are written to a temporary MEDIA_ROOT so image tests never
    touch the configured media location.
    """

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
            "admin_api:portfolio:list"
        )

        self.add_url = reverse(
            "admin_api:portfolio:add"
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
        portfolio,
    ):
        return self._portfolio_url(
            "detail",
            portfolio,
        )

    def update_url(
        self,
        portfolio,
    ):
        return self._portfolio_url(
            "update",
            portfolio,
        )

    def delete_url(
        self,
        portfolio,
    ):
        return self._portfolio_url(
            "delete",
            portfolio,
        )

    def image_add_url(
        self,
        portfolio,
    ):
        return self._portfolio_url(
            "image_add",
            portfolio,
        )

    def image_update_url(
        self,
        image_id,
    ):
        return reverse(
            (
                "admin_api:portfolio"
                ":image_update"
            ),
            kwargs={
                "image_id": image_id,
            },
        )

    def image_delete_url(
        self,
        image_id,
    ):
        return reverse(
            (
                "admin_api:portfolio"
                ":image_delete"
            ),
            kwargs={
                "image_id": image_id,
            },
        )

    def document_add_url(
        self,
        portfolio,
    ):
        return self._portfolio_url(
            "document_add",
            portfolio,
        )

    def document_update_url(
        self,
        document_id,
    ):
        return reverse(
            (
                "admin_api:portfolio"
                ":document_update"
            ),
            kwargs={
                "document_id":
                    document_id,
            },
        )

    def document_delete_url(
        self,
        document_id,
    ):
        return reverse(
            (
                "admin_api:portfolio"
                ":document_delete"
            ),
            kwargs={
                "document_id":
                    document_id,
            },
        )

    def repository_add_url(
        self,
        portfolio,
    ):
        return self._portfolio_url(
            "repository_add",
            portfolio,
        )

    def repository_update_url(
        self,
        repository_id,
    ):
        return reverse(
            (
                "admin_api:portfolio"
                ":repository_update"
            ),
            kwargs={
                "repository_id":
                    repository_id,
            },
        )

    def repository_delete_url(
        self,
        repository_id,
    ):
        return reverse(
            (
                "admin_api:portfolio"
                ":repository_delete"
            ),
            kwargs={
                "repository_id":
                    repository_id,
            },
        )

    def post_json(
        self,
        url,
        payload,
    ):
        return self.client.post(
            url,
            data=json.dumps(
                payload
            ),
            content_type=(
                "application/json"
            ),
            **self.csrf_headers(),
        )

    def patch_json(
        self,
        url,
        payload,
    ):
        return self.client.patch(
            url,
            data=json.dumps(
                payload
            ),
            content_type=(
                "application/json"
            ),
            **self.csrf_headers(),
        )

    def delete_request(
        self,
        url,
    ):
        return self.client.delete(
            url,
            **self.csrf_headers(),
        )

    def post_multipart(
        self,
        url,
        data,
    ):
        return self.client.post(
            url,
            data=data,
            **self.csrf_headers(),
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

    def create_portfolio(
        self,
        name="NEXCODE Platform",
        **overrides,
    ):
        fields = {
            "name": name,
            "category": (
                Portfolio.Category
                .WEB_APPLICATION
            ),
            "project_type": (
                Portfolio.ProjectType
                .CLIENT_PROJECT
            ),
        }

        fields.update(overrides)

        return (
            Portfolio.objects.create(
                **fields
            )
        )

    def _portfolio_url(
        self,
        name,
        portfolio,
    ):
        return reverse(
            f"admin_api:portfolio:{name}",
            kwargs={
                "portfolio_id":
                    portfolio.pk,
            },
        )
