from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from home.models import (
    PaymentAgreement,
    PaymentAllocation,
    PaymentInstallment,
    PaymentRecord,
    Portfolio,
)
from home.services.payment.status import (
    PaymentState,
    TimingState,
    get_agreement_summary,
    get_installment_status,
)


class PaymentStatusTests(
    TestCase
):
    def setUp(self):
        self.portfolio = (
            Portfolio.objects.create(
                name=(
                    "Finance Project"
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

        self.agreement = (
            PaymentAgreement
            .objects
            .create(
                portfolio=(
                    self.portfolio
                ),
                title=(
                    "Development "
                    "Contract"
                ),
                total_amount=(
                    Decimal(
                        "1000000.00"
                    )
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

        self.installment = (
            PaymentInstallment
            .objects
            .create(
                agreement=(
                    self.agreement
                ),
                sequence=1,
                title=(
                    "October "
                    "installment"
                ),
                amount=Decimal(
                    "1000000.00"
                ),
                due_type=(
                    PaymentInstallment
                    .DueType
                    .FIXED_DATE
                ),
                expected_due_date=(
                    date(
                        2026,
                        10,
                        1,
                    )
                ),
                due_date=date(
                    2026,
                    10,
                    1,
                ),
            )
        )

    def test_unpaid_future_installment_is_upcoming(
        self,
    ):
        status = (
            get_installment_status(
                self.installment,
                on_date=date(
                    2026,
                    9,
                    20,
                ),
            )
        )

        self.assertEqual(
            status.payment_state,
            PaymentState.UNPAID,
        )

        self.assertEqual(
            status.timing_state,
            TimingState.UPCOMING,
        )

        self.assertEqual(
            status.outstanding_amount,
            Decimal(
                "1000000.00"
            ),
        )

    def test_partial_payment_can_be_overdue(
        self,
    ):
        payment = (
            PaymentRecord
            .objects
            .create(
                agreement=(
                    self.agreement
                ),
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
                    self.installment
                ),
                amount=Decimal(
                    "400000.00"
                ),
            )
        )

        status = (
            get_installment_status(
                self.installment,
                on_date=date(
                    2026,
                    10,
                    10,
                ),
            )
        )

        self.assertEqual(
            status.payment_state,
            PaymentState.PARTIAL,
        )

        self.assertEqual(
            status.timing_state,
            TimingState.OVERDUE,
        )

        self.assertEqual(
            status.paid_amount,
            Decimal(
                "400000.00"
            ),
        )

        self.assertEqual(
            status.outstanding_amount,
            Decimal(
                "600000.00"
            ),
        )

    def test_voided_payment_is_not_counted(
        self,
    ):
        payment = (
            PaymentRecord
            .objects
            .create(
                agreement=(
                    self.agreement
                ),
                amount=Decimal(
                    "500000.00"
                ),
                currency="RWF",
                status=(
                    PaymentRecord
                    .Status.VOIDED
                ),
                voided_at=(
                    timezone.now()
                ),
                void_reason=(
                    "Duplicate "
                    "transaction"
                ),
            )
        )

        (
            PaymentAllocation
            .objects
            .create(
                payment=payment,
                installment=(
                    self.installment
                ),
                amount=Decimal(
                    "500000.00"
                ),
            )
        )

        status = (
            get_installment_status(
                self.installment,
                on_date=date(
                    2026,
                    10,
                    10,
                ),
            )
        )

        self.assertEqual(
            status.paid_amount,
            Decimal(
                "0.00"
            ),
        )

        self.assertEqual(
            status.payment_state,
            PaymentState.UNPAID,
        )

    def test_waived_installment_has_no_outstanding_balance(
        self,
    ):
        self.installment.is_waived = (
            True
        )

        self.installment.waived_at = (
            timezone.now()
        )

        self.installment.waiver_reason = (
            "Commercial waiver"
        )

        self.installment.save()

        status = (
            get_installment_status(
                self.installment
            )
        )

        self.assertEqual(
            status.payment_state,
            PaymentState.WAIVED,
        )

        self.assertEqual(
            status.timing_state,
            TimingState.SETTLED,
        )

        self.assertEqual(
            status.outstanding_amount,
            Decimal(
                "0.00"
            ),
        )

    def test_unconfirmed_milestone_waits_for_milestone(
        self,
    ):
        milestone = (
            PaymentInstallment
            .objects
            .create(
                agreement=(
                    self.agreement
                ),
                sequence=2,
                title=(
                    "Handover "
                    "payment"
                ),
                installment_type=(
                    PaymentInstallment
                    .Type.MILESTONE
                ),
                amount=Decimal(
                    "500000.00"
                ),
                due_type=(
                    PaymentInstallment
                    .DueType.MILESTONE
                ),
                expected_due_date=(
                    date(
                        2026,
                        12,
                        15,
                    )
                ),
                milestone=(
                    "Project handover"
                ),
            )
        )

        status = (
            get_installment_status(
                milestone,
                on_date=date(
                    2026,
                    12,
                    20,
                ),
            )
        )

        self.assertEqual(
            status.timing_state,
            (
                TimingState
                .AWAITING_MILESTONE
            ),
        )

    def test_agreement_summary_tracks_unallocated_money(
        self,
    ):
        payment = (
            PaymentRecord
            .objects
            .create(
                agreement=(
                    self.agreement
                ),
                amount=Decimal(
                    "500000.00"
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
                    self.installment
                ),
                amount=Decimal(
                    "300000.00"
                ),
            )
        )

        summary = (
            get_agreement_summary(
                self.agreement
            )
        )

        self.assertEqual(
            summary.received_amount,
            Decimal(
                "500000.00"
            ),
        )

        self.assertEqual(
            summary.allocated_amount,
            Decimal(
                "300000.00"
            ),
        )

        self.assertEqual(
            summary.unallocated_amount,
            Decimal(
                "200000.00"
            ),
        )

        self.assertEqual(
            summary.outstanding_amount,
            Decimal(
                "500000.00"
            ),
        )