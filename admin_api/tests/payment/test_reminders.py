from django.urls import reverse
from django.utils import timezone

from home.models import (
    PaymentNotification,
    PaymentReminderRule,
)

from admin_api.tests.payment.base import (
    PaymentApiTestCase,
)


class PaymentReminderApiTests(
    PaymentApiTestCase
):
    def test_admin_can_create_reminder_rule(
        self,
    ):
        self.login_admin()

        agreement = (
            self.create_agreement()
        )

        response = self.post_json(
            reverse(
                (
                    "admin_api:payment:"
                    "reminder_rule_add"
                ),
                kwargs={
                    "agreement_id":
                        agreement.pk,
                },
            ),
            {
                "event":
                    "installment_due",

                "timing":
                    "before",

                "days":
                    7,

                "channel":
                    "in_app",
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertTrue(
            PaymentReminderRule
            .objects
            .filter(
                agreement=agreement,
                days=7,
            )
            .exists()
        )

    def test_duplicate_rule_is_rejected(
        self,
    ):
        self.login_admin()

        agreement = (
            self.create_agreement()
        )

        payload = {
            "event":
                "installment_due",
            "timing":
                "before",
            "days": 7,
            "channel":
                "in_app",
        }

        url = reverse(
            (
                "admin_api:payment:"
                "reminder_rule_add"
            ),
            kwargs={
                "agreement_id":
                    agreement.pk,
            },
        )

        self.post_json(
            url,
            payload,
        )

        response = self.post_json(
            url,
            payload,
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_notification_list_is_scoped_to_admin(
        self,
    ):
        self.login_admin()

        agreement = (
            self.create_agreement()
        )

        other_user = (
            type(
                self.admin_user
            )
            .objects
            .create_user(
                username=(
                    "other@nexcode.africa"
                ),
                password=(
                    self.password
                ),
            )
        )

        for recipient in (
            self.admin_user,
            other_user,
        ):
            PaymentNotification.objects.create(
                agreement=agreement,
                recipient_user=(
                    recipient
                ),
                event=(
                    "installment_due"
                ),
                channel="in_app",
                title="Payment due",
                message=(
                    "Payment reminder"
                ),
                target_date=(
                    timezone
                    .localdate()
                ),
                trigger_date=(
                    timezone
                    .localdate()
                ),
                status="sent",
                dedupe_key=(
                    f"notification-"
                    f"{recipient.pk}"
                ),
            )

        response = self.client.get(
            reverse(
                (
                    "admin_api:payment:"
                    "reminder_"
                    "notification_list"
                )
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        items = response.json()[
            "data"
        ]["items"]

        self.assertEqual(
            len(items),
            1,
        )

    def test_notification_can_be_marked_read(
        self,
    ):
        self.login_admin()

        agreement = (
            self.create_agreement()
        )

        notification = (
            PaymentNotification
            .objects
            .create(
                agreement=agreement,
                recipient_user=(
                    self.admin_user
                ),
                event=(
                    "installment_due"
                ),
                channel="in_app",
                title="Payment due",
                message=(
                    "Payment reminder"
                ),
                target_date=(
                    timezone
                    .localdate()
                ),
                trigger_date=(
                    timezone
                    .localdate()
                ),
                status="sent",
                dedupe_key=(
                    "mark-read-test"
                ),
            )
        )

        response = self.post_json(
            reverse(
                (
                    "admin_api:payment:"
                    "reminder_"
                    "notification_read"
                ),
                kwargs={
                    "notification_id":
                        notification.pk,
                },
            ),
            {},
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        notification.refresh_from_db()

        self.assertIsNotNone(
            notification.read_at
        )