from admin_api.constants import NEXCODE_ADMIN_LOGIN_MAX_FAILURES
from admin_api.tests.auth.base import AuthApiTestCase


class NexcodeAdminThrottleTests(AuthApiTestCase):
    def test_login_is_throttled_after_repeated_failures(self):
        for _ in range(
            NEXCODE_ADMIN_LOGIN_MAX_FAILURES - 1
        ):
            response = self.login(
                self.admin_user.email,
                password="WrongPassword123!",
            )

            self.assertEqual(
                response.status_code,
                401,
            )

        response = self.login(
            self.admin_user.email,
            password="WrongPassword123!",
        )

        self.assertEqual(
            response.status_code,
            429,
        )

        self.assertIn(
            "Retry-After",
            response,
        )

    def test_blocked_login_rejects_correct_password(self):
        for _ in range(
            NEXCODE_ADMIN_LOGIN_MAX_FAILURES
        ):
            response = self.login(
                self.admin_user.email,
                password="WrongPassword123!",
            )

        self.assertEqual(
            response.status_code,
            429,
        )

        response = self.login(
            self.admin_user.email,
            password=self.password,
        )

        self.assertEqual(
            response.status_code,
            429,
        )

    def test_successful_login_resets_failure_counter(self):
        for _ in range(
            NEXCODE_ADMIN_LOGIN_MAX_FAILURES - 1
        ):
            response = self.login(
                self.admin_user.email,
                password="WrongPassword123!",
            )

            self.assertEqual(
                response.status_code,
                401,
            )

        response = self.login(
            self.admin_user.email,
            password=self.password,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        response = self.login(
            self.admin_user.email,
            password="WrongPassword123!",
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_throttle_does_not_expose_account_existence(self):
        unknown_email = (
            "unknown-user@nexcode.africa"
        )

        for _ in range(
            NEXCODE_ADMIN_LOGIN_MAX_FAILURES - 1
        ):
            response = self.login(
                unknown_email,
                password="WrongPassword123!",
            )

            self.assertEqual(
                response.status_code,
                401,
            )

        response = self.login(
            unknown_email,
            password="WrongPassword123!",
        )

        self.assertEqual(
            response.status_code,
            429,
        )

    def test_throttle_is_scoped_by_email(self):
        for _ in range(
            NEXCODE_ADMIN_LOGIN_MAX_FAILURES
        ):
            self.login(
                self.admin_user.email,
                password="WrongPassword123!",
            )

        response = self.login(
            self.regular_user.email,
            password="WrongPassword123!",
        )

        self.assertEqual(
            response.status_code,
            401,
        )

