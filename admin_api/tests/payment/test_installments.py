from datetime import date
from decimal import Decimal

from django.urls import reverse

from home.models import (
    PaymentAllocation,
    PaymentRecord,
)

from admin_api.tests.payment.base import (
    PaymentApiTestCase,
)


class PaymentInstallmentApiTests(
    PaymentApiTestCase
):
    def test_milestone_date_can_be_confirmed(
        self,
    ):
        self.login_admin()

        agreement = (
            self.create_agreement()
        )

        installment = (
            self.create_installment(
                agreement,
                due_type="milestone",
                due_date=None,
                milestone=(
                    "Project handover"
                ),
            )
        )

        response = self.post_json(
            reverse(
                (
                    "admin_api:payment:"
                    "installment_"
                    "confirm_milestone"
                ),
                kwargs={
                    "installment_id":
                        installment.pk,
                },
            ),
            {
                "due_date":
                    "2026-12-20",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        installment.refresh_from_db()

        self.assertEqual(
            installment.due_date,
            date(
                2026,
                12,
                20,
            ),
        )

    def test_paid_installment_cannot_be_waived(
        self,
    ):
        self.login_admin()

        agreement = (
            self.create_agreement()
        )

        installment = (
            self.create_installment(
                agreement
            )
        )

        payment = (
            PaymentRecord
            .objects
            .create(
                agreement=agreement,
                amount=Decimal(
                    "100000.00"
                ),
                currency="RWF",
            )
        )

        (
            PaymentAllocation
            .objects
            .create(
                payment=payment,
                installment=(
                    installment
                ),
                amount=Decimal(
                    "100000.00"
                ),
            )
        )

        response = self.post_json(
            reverse(
                (
                    "admin_api:payment:"
                    "installment_waive"
                ),
                kwargs={
                    "installment_id":
                        installment.pk,
                },
            ),
            {
                "reason":
                    "Commercial waiver",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )