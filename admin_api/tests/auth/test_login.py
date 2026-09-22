import json

from admin_api.tests.auth.base import AuthApiTestCase


class NexcodeAdminLoginTests(AuthApiTestCase):
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

