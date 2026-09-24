from decimal import Decimal

from django.urls import reverse

from home.models import (
    PaymentRecord,
)

from admin_api.tests.payment.base import (
    PaymentApiTestCase,
)


class PaymentRecordApiTests(
    PaymentApiTestCase
):
    def test_payment_can_be_recorded_and_allocated(
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

        response = self.post_json(
            reverse(
                "admin_api:payment:"
                "record_add",
                kwargs={
                    "agreement_id":
                        agreement.pk,
                },
            ),
            {
                "amount":
                    "400000.00",

                "currency":
                    "RWF",

                "payment_method":
                    "bank_transfer",

                "reference":
                    "BK-12345",

                "allocations": [
                    {
                        "installment_id":
                            installment.pk,

                        "amount":
                            "400000.00",
                    },
                ],
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        payment = (
            PaymentRecord
            .objects
            .get()
        )

        self.assertEqual(
            payment.amount,
            Decimal(
                "400000.00"
            ),
        )

        self.assertEqual(
            payment
            .allocations
            .get()
            .amount,
            Decimal(
                "400000.00"
            ),
        )

    def test_payment_cannot_be_overallocated(
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

        response = self.post_json(
            reverse(
                "admin_api:payment:"
                "record_add",
                kwargs={
                    "agreement_id":
                        agreement.pk,
                },
            ),
            {
                "amount":
                    "100000.00",

                "allocations": [
                    {
                        "installment_id":
                            installment.pk,

                        "amount":
                            "200000.00",
                    },
                ],
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertFalse(
            PaymentRecord
            .objects
            .exists()
        )

    def test_payment_is_voided_not_deleted(
        self,
    ):
        self.login_admin()

        agreement = (
            self.create_agreement()
        )

        payment = (
            PaymentRecord
            .objects
            .create(
                agreement=agreement,
                amount=Decimal(
                    "200000.00"
                ),
                currency="RWF",
            )
        )

        response = self.post_json(
            reverse(
                "admin_api:payment:"
                "record_void",
                kwargs={
                    "payment_id":
                        payment.pk,
                },
            ),
            {
                "reason":
                    "Duplicate entry",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        payment.refresh_from_db()

        self.assertEqual(
            payment.status,
            (
                PaymentRecord
                .Status.VOIDED
            ),
        )

        self.assertTrue(
            PaymentRecord
            .objects
            .filter(
                pk=payment.pk
            )
            .exists()
        )