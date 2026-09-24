from decimal import Decimal

from django.urls import reverse

from home.models import (
    PaymentAllocation,
    PaymentRecord,
)

from admin_api.tests.payment.base import (
    PaymentApiTestCase,
)


class PaymentSummaryApiTests(
    PaymentApiTestCase
):
    def test_agreement_summary_reports_balance(
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
                    "400000.00"
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
                    "400000.00"
                ),
            )
        )

        response = self.client.get(
            reverse(
                "admin_api:payment:"
                "summary_agreement",
                kwargs={
                    "agreement_id":
                        agreement.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        summary = response.json()[
            "data"
        ]["summary"]

        self.assertEqual(
            summary[
                "received_amount"
            ],
            "400000.00",
        )

        self.assertEqual(
            summary[
                "outstanding_amount"
            ],
            "600000.00",
        )

    def test_portfolio_summary_combines_agreements(
        self,
    ):
        self.login_admin()

        self.create_agreement()

        response = self.client.get(
            reverse(
                "admin_api:payment:"
                "summary_portfolio",
                kwargs={
                    "portfolio_id":
                        self.portfolio.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        summary = response.json()[
            "data"
        ]["summary"]

        self.assertEqual(
            summary[
                "total_contracted"
            ],
            "1000000.00",
        )