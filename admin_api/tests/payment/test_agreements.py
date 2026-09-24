from django.urls import reverse

from home.models import (
    PaymentAgreement,
)

from admin_api.tests.payment.base import (
    PaymentApiTestCase,
)


class PaymentAgreementApiTests(
    PaymentApiTestCase
):
    def test_admin_can_create_agreement(
        self,
    ):
        self.login_admin()

        response = self.post_json(
            reverse(
                "admin_api:payment:"
                "agreement_add"
            ),
            {
                "portfolio_id":
                    self.portfolio.pk,

                "title":
                    "Website Contract",

                "agreement_type":
                    "project",

                "currency":
                    "RWF",

                "total_amount":
                    "5000000.00",

                "agreement_date":
                    "2026-09-01",

                "start_date":
                    "2026-09-05",

                "status":
                    "active",
            },
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            PaymentAgreement
            .objects
            .count(),
            1,
        )

    def test_list_requires_authentication(
        self,
    ):
        response = self.client.get(
            reverse(
                "admin_api:payment:"
                "agreement_list"
            )
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_cannot_delete_active_agreement(
        self,
    ):
        self.login_admin()

        agreement = (
            self.create_agreement()
        )

        response = (
            self.client.delete(
                reverse(
                    "admin_api:payment:"
                    "agreement_delete",
                    kwargs={
                        "agreement_id":
                            agreement.pk,
                    },
                ),
                **self.csrf_headers(),
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertTrue(
            PaymentAgreement
            .objects
            .filter(
                pk=agreement.pk
            )
            .exists()
        )