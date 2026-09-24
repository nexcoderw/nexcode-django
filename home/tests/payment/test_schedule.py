from datetime import date
from decimal import Decimal

from django.core.exceptions import (
    ValidationError,
)
from django.test import TestCase

from home.models import (
    PaymentAgreement,
    PaymentInstallment,
    Portfolio,
)
from home.services.payment.schedule import (
    InstallmentPlanItem,
    add_months,
    build_contract_schedule,
    build_maintenance_schedule,
    create_installment_schedule,
    split_amount_evenly,
)


class PaymentScheduleTests(
    TestCase
):
    def create_agreement(
        self,
        total_amount,
    ):
        portfolio = (
            Portfolio.objects.create(
                name=(
                    "Scheduled "
                    "Project"
                ),
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

        return (
            PaymentAgreement
            .objects
            .create(
                portfolio=portfolio,
                title=(
                    "Project Contract"
                ),
                total_amount=(
                    total_amount
                ),
                agreement_date=date(
                    2026,
                    9,
                    1,
                ),
                start_date=date(
                    2026,
                    9,
                    1,
                ),
                status=(
                    PaymentAgreement
                    .Status.ACTIVE
                ),
            )
        )

    def test_even_split_keeps_exact_total(
        self,
    ):
        amounts = (
            split_amount_evenly(
                Decimal(
                    "100.00"
                ),
                3,
            )
        )

        self.assertEqual(
            amounts,
            (
                Decimal(
                    "33.33"
                ),
                Decimal(
                    "33.33"
                ),
                Decimal(
                    "33.34"
                ),
            ),
        )

        self.assertEqual(
            sum(amounts),
            Decimal(
                "100.00"
            ),
        )

    def test_calendar_months_preserve_original_day_where_possible(
        self,
    ):
        start = date(
            2027,
            1,
            31,
        )

        self.assertEqual(
            add_months(
                start,
                1,
            ),
            date(
                2027,
                2,
                28,
            ),
        )

        self.assertEqual(
            add_months(
                start,
                2,
            ),
            date(
                2027,
                3,
                31,
            ),
        )

    def test_contract_schedule_supports_down_payment_and_monthly_installments(
        self,
    ):
        schedule = (
            build_contract_schedule(
                total_amount=(
                    Decimal(
                        "10000000.00"
                    )
                ),
                down_payment_amount=(
                    Decimal(
                        "2000000.00"
                    )
                ),
                down_payment_date=(
                    date(
                        2026,
                        9,
                        5,
                    )
                ),
                installment_count=4,
                first_installment_date=(
                    date(
                        2026,
                        10,
                        5,
                    )
                ),
            )
        )

        self.assertEqual(
            len(schedule),
            5,
        )

        self.assertEqual(
            schedule[0]
            .installment_type,
            (
                PaymentInstallment
                .Type.DOWN_PAYMENT
            ),
        )

        self.assertEqual(
            schedule[0].amount,
            Decimal(
                "2000000.00"
            ),
        )

        self.assertEqual(
            [
                item.amount
                for item
                in schedule[1:]
            ],
            [
                Decimal(
                    "2000000.00"
                ),
            ] * 4,
        )

        self.assertEqual(
            sum(
                (
                    item.amount
                    for item
                    in schedule
                ),
                Decimal(
                    "0.00"
                ),
            ),
            Decimal(
                "10000000.00"
            ),
        )

    def test_maintenance_schedule_creates_each_month(
        self,
    ):
        schedule = (
            build_maintenance_schedule(
                monthly_amount=(
                    Decimal(
                        "200000.00"
                    )
                ),
                months=12,
                first_due_date=(
                    date(
                        2027,
                        1,
                        1,
                    )
                ),
            )
        )

        self.assertEqual(
            len(schedule),
            12,
        )

        self.assertTrue(
            all(
                item
                .installment_type
                == (
                    PaymentInstallment
                    .Type
                    .MAINTENANCE
                )
                for item
                in schedule
            )
        )

        self.assertEqual(
            schedule[-1]
            .due_date,
            date(
                2027,
                12,
                1,
            ),
        )

        self.assertEqual(
            sum(
                (
                    item.amount
                    for item
                    in schedule
                ),
                Decimal(
                    "0.00"
                ),
            ),
            Decimal(
                "2400000.00"
            ),
        )

    def test_schedule_must_match_agreement_total(
        self,
    ):
        agreement = (
            self.create_agreement(
                Decimal(
                    "1000000.00"
                )
            )
        )

        items = (
            InstallmentPlanItem(
                sequence=1,
                title=(
                    "Down payment"
                ),
                installment_type=(
                    PaymentInstallment
                    .Type
                    .DOWN_PAYMENT
                ),
                amount=Decimal(
                    "500000.00"
                ),
                due_type=(
                    PaymentInstallment
                    .DueType
                    .FIXED_DATE
                ),
                expected_due_date=(
                    date(
                        2026,
                        9,
                        5,
                    )
                ),
                due_date=date(
                    2026,
                    9,
                    5,
                ),
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            create_installment_schedule(
                agreement,
                items,
            )

    def test_existing_schedule_is_not_silently_replaced(
        self,
    ):
        agreement = (
            self.create_agreement(
                Decimal(
                    "1000000.00"
                )
            )
        )

        schedule = (
            build_contract_schedule(
                total_amount=(
                    Decimal(
                        "1000000.00"
                    )
                ),
                down_payment_amount=(
                    Decimal(
                        "200000.00"
                    )
                ),
                down_payment_date=(
                    date(
                        2026,
                        9,
                        5,
                    )
                ),
                installment_count=2,
                first_installment_date=(
                    date(
                        2026,
                        10,
                        5,
                    )
                ),
            )
        )

        create_installment_schedule(
            agreement,
            schedule,
        )

        with self.assertRaises(
            ValidationError
        ):
            create_installment_schedule(
                agreement,
                schedule,
            )