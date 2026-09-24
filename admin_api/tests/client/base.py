import json

from django.contrib.auth import (
    get_user_model,
)
from django.contrib.auth.models import (
    Group,
)
from django.test import (
    Client as DjangoClient,
    TestCase,
)
from django.urls import reverse

from admin_api.constants import (
    NEXCODE_ADMIN_GROUP_NAME,
)
from home.models import Client


class ClientApiTestCase(
    TestCase
):
    password = (
        "TestPassword123!"
    )

    def setUp(self):
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

        self.client = DjangoClient(
            enforce_csrf_checks=True,
        )

        self.csrf_url = reverse(
            "admin_api:auth:csrf"
        )

        self.list_url = reverse(
            "admin_api:client:list"
        )

        self.add_url = reverse(
            "admin_api:client:add"
        )

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
        client,
    ):
        return self._client_url(
            "detail",
            client,
        )

    def update_url(
        self,
        client,
    ):
        return self._client_url(
            "update",
            client,
        )

    def delete_url(
        self,
        client,
    ):
        return self._client_url(
            "delete",
            client,
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

    def create_client(
        self,
        name="Acme Rwanda",
        **overrides,
    ):
        fields = {
            "name": name,
            "email": "hello@acme.rw",
            "phone_number": (
                "+250 788 000 000"
            ),
        }

        fields.update(overrides)

        return Client.objects.create(
            **fields
        )

    def _client_url(
        self,
        name,
        client,
    ):
        return reverse(
            f"admin_api:client:{name}",
            kwargs={
                "client_id":
                    client.pk,
            },
        )
