from datetime import (
    date,
    datetime,
    timezone as dt_timezone,
)
from decimal import Decimal

from django.urls import reverse

from admin_api.tests.payment.base import (
    PaymentApiTestCase,
)
from home.models import (
    PaymentAgreement,
    PaymentAllocation,
    PaymentRecord,
    Portfolio,
)


class PaymentReportApiTests(
    PaymentApiTestCase
):
    def setUp(self):
        super().setUp()

        self.login_admin()

    def test_overview_separates_currencies(
        self,
    ):
        self.create_agreement(
            total_amount=Decimal(
                "1000000.00"
            ),
            currency="RWF",
        )

        other_portfolio = (
            Portfolio.objects.create(
                name="USD Project",
                category=(
                    Portfolio.Category
                    .WEB_APPLICATION
                ),
                project_type=(
                    Portfolio
                    .ProjectType
                    .CLIENT_PROJECT
                ),
            )
        )

        self.create_agreement(
            portfolio=(
                other_portfolio
            ),
            total_amount=Decimal(
                "1000.00"
            ),
            currency="USD",
        )

        response = (
            self.client.get(
                reverse(
                    (
                        "admin_api:"
                        "payment:"
                        "report_overview"
                    )
                )
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        currencies = {
            row["currency"]:
                row
            for row
            in response.json()[
                "data"
            ][
                "overview"
            ][
                "currencies"
            ]
        }

        self.assertEqual(
            currencies[
                "RWF"
            ][
                "total_contracted"
            ],
            "1000000.00",
        )

        self.assertEqual(
            currencies[
                "USD"
            ][
                "total_contracted"
            ],
            "1000.00",
        )

    def test_collections_exclude_voided_payments(
        self,
    ):
        agreement = (
            self.create_agreement()
        )

        PaymentRecord.objects.create(
            agreement=agreement,
            amount=Decimal(
                "300000.00"
            ),
            currency="RWF",
            paid_at=datetime(
                2026,
                9,
                4,
                tzinfo=dt_timezone.utc,
            ),
            status=(
                PaymentRecord
                .Status.POSTED
            ),
        )

        PaymentRecord.objects.create(
            agreement=agreement,
            amount=Decimal(
                "200000.00"
            ),
            currency="RWF",
            paid_at=datetime(
                2026,
                9,
                5,
                tzinfo=dt_timezone.utc,
            ),
            status=(
                PaymentRecord
                .Status.VOIDED
            ),
            voided_at=datetime(
                2026,
                9,
                6,
                tzinfo=dt_timezone.utc,
            ),
            void_reason=(
                "Duplicate entry"
            ),
        )

        response = (
            self.client.get(
                reverse(
                    (
                        "admin_api:"
                        "payment:"
                        "report_collections"
                    )
                )
            )
        )

        rows = response.json()[
            "data"
        ][
            "report"
        ][
            "rows"
        ]

        self.assertEqual(
            len(rows),
            1,
        )

        self.assertEqual(
            rows[0]["amount"],
            "300000.00",
        )

        self.assertEqual(
            rows[0][
                "payment_count"
            ],
            1,
        )

    def test_outstanding_report_identifies_overdue_balance(
        self,
    ):
        agreement = (
            self.create_agreement()
        )

        installment = (
            self.create_installment(
                agreement,
                amount=Decimal(
                    "1000000.00"
                ),
                expected_due_date=date(
                    2026,
                    9,
                    1,
                ),
                due_date=date(
                    2026,
                    9,
                    1,
                ),
            )
        )

        payment = (
            PaymentRecord.objects.create(
                agreement=agreement,
                amount=Decimal(
                    "250000.00"
                ),
                currency="RWF",
            )
        )

        PaymentAllocation.objects.create(
            payment=payment,
            installment=installment,
            amount=Decimal(
                "250000.00"
            ),
        )

        response = (
            self.client.get(
                reverse(
                    (
                        "admin_api:"
                        "payment:"
                        "report_outstanding"
                    )
                ),
                {
                    "kind":
                        "overdue",

                    "as_of":
                        "2026-09-25",
                },
            )
        )

        rows = response.json()[
            "data"
        ][
            "report"
        ][
            "rows"
        ]

        self.assertEqual(
            len(rows),
            1,
        )

        self.assertEqual(
            rows[0][
                "outstanding_amount"
            ],
            "750000.00",
        )

        self.assertEqual(
            rows[0][
                "timing_state"
            ],
            "overdue",
        )

    def test_statement_is_scoped_to_portfolio(
        self,
    ):
        agreement = (
            self.create_agreement()
        )

        payment = (
            PaymentRecord.objects.create(
                agreement=agreement,
                amount=Decimal(
                    "200000.00"
                ),
                currency="RWF",
            )
        )

        response = (
            self.client.get(
                reverse(
                    (
                        "admin_api:"
                        "payment:"
                        "report_statement"
                    ),
                    kwargs={
                        "portfolio_id":
                            self
                            .portfolio
                            .pk,
                    },
                )
            )
        )

        statement = response.json()[
            "data"
        ][
            "statement"
        ]

        self.assertEqual(
            statement[
                "portfolio"
            ][
                "id"
            ],
            self.portfolio.pk,
        )

        self.assertEqual(
            statement[
                "payments"
            ][0][
                "id"
            ],
            payment.pk,
        )

    def test_receipt_pdf_is_generated(
        self,
    ):
        agreement = (
            self.create_agreement()
        )

        payment = (
            PaymentRecord.objects.create(
                agreement=agreement,
                amount=Decimal(
                    "500000.00"
                ),
                currency="RWF",
            )
        )

        response = (
            self.client.get(
                reverse(
                    (
                        "admin_api:"
                        "payment:"
                        "report_receipt"
                    ),
                    kwargs={
                        "payment_id":
                            payment.pk,
                    },
                ),
                {
                    "format":
                        "pdf",
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response[
                "Content-Type"
            ],
            "application/pdf",
        )

        self.assertTrue(
            response.content.startswith(
                b"%PDF"
            )
        )