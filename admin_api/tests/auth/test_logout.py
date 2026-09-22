import json

from admin_api.tests.auth.base import AuthApiTestCase


class NexcodeAdminLogoutTests(AuthApiTestCase):
    def test_logout_requires_post(self):
        self.client.force_login(
            self.admin_user
        )

        response = self.client.get(
            self.logout_url
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_logout_requires_csrf_token(self):
        csrf_token = self.get_csrf_token()

        login_response = self.client.post(
            self.login_url,
            data=json.dumps(
                {
                    "email": self.admin_user.email,
                    "password": self.password,
                }
            ),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            login_response.status_code,
            200,
        )

        response = self.client.post(
            self.logout_url
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_can_logout(self):
        login_response = self.login(
            self.admin_user.email
        )

        self.assertEqual(
            login_response.status_code,
            200,
        )

        self.assertIn(
            "_auth_user_id",
            self.client.session,
        )

        response = self.logout()

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["message"],
            "Signed out successfully.",
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )

    def test_me_is_unauthenticated_after_logout(self):
        login_response = self.login(
            self.admin_user.email
        )

        self.assertEqual(
            login_response.status_code,
            200,
        )

        logout_response = self.logout()

        self.assertEqual(
            logout_response.status_code,
            200,
        )

        response = self.client.get(
            self.me_url
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_logout_works_after_admin_access_is_revoked(self):
        login_response = self.login(
            self.admin_user.email
        )

        self.assertEqual(
            login_response.status_code,
            200,
        )

        self.admin_user.groups.remove(
            self.group
        )

        response = self.logout()

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )

    def test_logout_is_safe_when_already_logged_out(self):
        csrf_token = self.get_csrf_token()

        response = self.client.post(
            self.logout_url,
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

