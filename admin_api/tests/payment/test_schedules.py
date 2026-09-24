from decimal import Decimal

from django.urls import reverse

from home.models import (
    PaymentAgreement,
)

from admin_api.tests.payment.base import (
    PaymentApiTestCase,
)


class PaymentScheduleApiTests(
    PaymentApiTestCase
):
    def test_contract_schedule_is_generated(
        self,
    ):
        self.login_admin()

        agreement = (
            self.create_agreement(
                total_amount=(
                    Decimal(
                        "10000000.00"
                    )
                )
            )
        )

        response = self.post_json(
            reverse(
                "admin_api:payment:"
                "schedule_contract",
                kwargs={
                    "agreement_id":
                        agreement.pk,
                },
            ),
            {
                "down_payment_amount":
                    "2000000.00",

                "down_payment_date":
                    "2026-09-05",

                "installment_count":
                    4,

                "first_installment_date":
                    "2026-10-05",
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            agreement
            .installments
            .count(),
            5,
        )

    def test_maintenance_schedule_requires_maintenance_agreement(
        self,
    ):
        self.login_admin()

        agreement = (
            self.create_agreement()
        )

        response = self.post_json(
            reverse(
                "admin_api:payment:"
                "schedule_maintenance",
                kwargs={
                    "agreement_id":
                        agreement.pk,
                },
            ),
            {
                "monthly_amount":
                    "200000.00",

                "months":
                    12,

                "first_due_date":
                    "2027-01-01",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )