import json

from django.core import mail
from django.test import override_settings
from django.urls import reverse

from admin_api.tests.auth.base import AuthApiTestCase


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="NEXCODE <no-reply@example.com>",
)
class NexcodeAdminPasswordResetTests(AuthApiTestCase):
    def setUp(self):
        super().setUp()
        self.request_url = reverse("admin_api:auth:password-reset-request")
        self.verify_url = reverse("admin_api:auth:password-reset-verify")
        self.confirm_url = reverse("admin_api:auth:password-reset-confirm")

    def post_json(self, url, payload):
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=self.get_csrf_token(),
        )

    def test_request_rejects_invalid_email(self):
        response = self.post_json(self.request_url, {"email": "invalid"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)

    def test_unknown_account_gets_generic_response(self):
        response = self.post_json(
            self.request_url, {"email": "unknown@example.com"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("challenge_id", response.json()["data"])
        self.assertEqual(len(mail.outbox), 0)

    def test_admin_can_reset_password_once(self):
        request_response = self.post_json(
            self.request_url, {"email": self.admin_user.email}
        )
        self.assertEqual(request_response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        challenge_id = request_response.json()["data"]["challenge_id"]
        code = mail.outbox[0].body.split("Verification code: ", 1)[1][:6]
        verify_response = self.post_json(
            self.verify_url, {"challenge_id": challenge_id, "code": code}
        )
        self.assertEqual(verify_response.status_code, 200)

        reset_token = verify_response.json()["data"]["reset_token"]
        password = "NewSecurePassword123!"
        payload = {
            "reset_token": reset_token,
            "password": password,
            "confirm_password": password,
        }
        confirm_response = self.post_json(self.confirm_url, payload)
        self.assertEqual(confirm_response.status_code, 200)
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.check_password(password))
        self.assertEqual(self.post_json(self.confirm_url, payload).status_code, 400)

    def test_confirm_rejects_mismatched_passwords(self):
        response = self.post_json(
            self.confirm_url,
            {
                "reset_token": "unused",
                "password": "NewSecurePassword123!",
                "confirm_password": "different",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("confirm_password", response.json()["errors"])
