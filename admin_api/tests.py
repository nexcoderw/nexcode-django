import json

from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.http import JsonResponse
from django.test import RequestFactory, TestCase

from admin_api.constants import NEXCODE_ADMIN_GROUP_NAME
from admin_api.permissions import (
    is_nexcode_admin,
    nexcode_admin_required,
)


class NexcodeAdminPermissionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.group = Group.objects.create(
            name=NEXCODE_ADMIN_GROUP_NAME,
        )

        User = get_user_model()

        self.admin_user = User.objects.create_user(
            username="admin@nexcode.africa",
            email="admin@nexcode.africa",
            password="TestPassword123!",
        )
        self.admin_user.groups.add(self.group)

        self.regular_user = User.objects.create_user(
            username="user@nexcode.africa",
            email="user@nexcode.africa",
            password="TestPassword123!",
        )

    def test_group_member_is_nexcode_admin(self):
        self.assertTrue(
            is_nexcode_admin(self.admin_user)
        )

    def test_regular_user_is_not_nexcode_admin(self):
        self.assertFalse(
            is_nexcode_admin(self.regular_user)
        )

    def test_anonymous_user_is_not_nexcode_admin(self):
        self.assertFalse(
            is_nexcode_admin(AnonymousUser())
        )

    def test_inactive_group_member_is_not_nexcode_admin(self):
        self.admin_user.is_active = False
        self.admin_user.save(
            update_fields=["is_active"]
        )

        self.assertFalse(
            is_nexcode_admin(self.admin_user)
        )

    def test_decorator_rejects_anonymous_request(self):
        @nexcode_admin_required
        def protected_view(request):
            return JsonResponse(
                {"status": "success"}
            )

        request = self.factory.get("/")
        request.user = AnonymousUser()

        response = protected_view(request)

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_decorator_rejects_non_admin_user(self):
        @nexcode_admin_required
        def protected_view(request):
            return JsonResponse(
                {"status": "success"}
            )

        request = self.factory.get("/")
        request.user = self.regular_user

        response = protected_view(request)

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_decorator_allows_nexcode_admin(self):
        @nexcode_admin_required
        def protected_view(request):
            return JsonResponse(
                {"status": "success"}
            )

        request = self.factory.get("/")
        request.user = self.admin_user

        response = protected_view(request)

        self.assertEqual(
            response.status_code,
            200,
        )

class NexcodeAdminLoginTests(TestCase):
    password = "TestPassword123!"

    def setUp(self):
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

    def test_csrf_endpoint_sets_cookie(self):
        response = self.client.get(
            self.csrf_url
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "csrftoken",
            response.cookies,
        )

    def test_login_requires_csrf_token(self):
        response = self.client.post(
            self.login_url,
            data=json.dumps(
                {
                    "email": (
                        self.admin_user.email
                    ),
                    "password": self.password,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_can_login(self):
        response = self.login(
            self.admin_user.email
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["data"][
                "admin"
            ]["email"],
            self.admin_user.email,
        )

        self.assertEqual(
            int(
                self.client.session[
                    "_auth_user_id"
                ]
            ),
            self.admin_user.pk,
        )

    def test_invalid_password_is_rejected(self):
        response = self.login(
            self.admin_user.email,
            password="WrongPassword123!",
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_regular_user_is_rejected(self):
        response = self.login(
            self.regular_user.email
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_inactive_admin_is_rejected(self):
        self.admin_user.is_active = False
        self.admin_user.save(
            update_fields=["is_active"]
        )

        response = self.login(
            self.admin_user.email
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_invalid_json_is_rejected(self):
        csrf_token = self.get_csrf_token()

        response = self.client.post(
            self.login_url,
            data="{invalid",
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            response.status_code,
            400,
        )