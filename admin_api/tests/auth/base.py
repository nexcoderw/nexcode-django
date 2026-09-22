import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from admin_api.constants import NEXCODE_ADMIN_GROUP_NAME


class AuthApiTestCase(TestCase):
    password = "TestPassword123!"

    def setUp(self):
        cache.clear()
        User = get_user_model()

        self.group, _ = Group.objects.get_or_create(
            name=NEXCODE_ADMIN_GROUP_NAME,
        )

        self.admin_user = User.objects.create_user(
            username="admin@nexcode.africa",
            email="admin@nexcode.africa",
            password=self.password,
            first_name="Nexcode",
            last_name="Admin",
        )

        self.admin_user.groups.add(
            self.group
        )

        self.regular_user = User.objects.create_user(
            username="user@nexcode.africa",
            email="user@nexcode.africa",
            password=self.password,
        )

        self.client = Client(
            enforce_csrf_checks=True,
        )

        self.csrf_url = reverse(
            "admin_api:auth:csrf"
        )

        self.login_url = reverse(
            "admin_api:auth:login"
        )

        self.me_url = reverse(
            "admin_api:auth:me"
        )

        self.logout_url = reverse(
            "admin_api:auth:logout"
        )

    def get_csrf_token(self):
        response = self.client.get(
            self.csrf_url
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        return response.json()["data"][
            "csrf_token"
        ]

    def login(self, email, password=None):
        csrf_token = self.get_csrf_token()

        return self.client.post(
            self.login_url,
            data=json.dumps(
                {
                    "email": email,
                    "password": (
                        password
                        or self.password
                    ),
                }
            ),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

    def logout(self):
        csrf_token = self.get_csrf_token()

        return self.client.post(
            self.logout_url,
            HTTP_X_CSRFTOKEN=csrf_token,
        )

