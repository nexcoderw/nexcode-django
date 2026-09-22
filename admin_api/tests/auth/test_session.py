from admin_api.tests.auth.base import AuthApiTestCase


class NexcodeAdminSessionTests(AuthApiTestCase):
    def test_me_requires_authentication(self):
        response = self.client.get(
            self.me_url
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_me_returns_authenticated_admin(self):
        login_response = self.login(
            self.admin_user.email
        )

        self.assertEqual(
            login_response.status_code,
            200,
        )

        response = self.client.get(
            self.me_url
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()["data"]["admin"]

        self.assertEqual(
            data["id"],
            self.admin_user.pk,
        )

        self.assertEqual(
            data["email"],
            self.admin_user.email,
        )

        self.assertEqual(
            data["first_name"],
            self.admin_user.first_name,
        )

        self.assertEqual(
            data["last_name"],
            self.admin_user.last_name,
        )

    def test_me_rejects_regular_authenticated_user(self):
        self.client.force_login(
            self.regular_user
        )

        response = self.client.get(
            self.me_url
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_me_does_not_allow_post(self):
        self.client.force_login(
            self.admin_user
        )

        response = self.client.post(
            self.me_url,
        )

        self.assertEqual(
            response.status_code,
            405,
        )

