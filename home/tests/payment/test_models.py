from datetime import date
from decimal import Decimal

from django.core.exceptions import (
    ValidationError,
)
from django.db import (
    IntegrityError,
    transaction,
)
from django.db.models.deletion import (
    ProtectedError,
)
from django.test import TestCase
from django.utils import timezone

from home.models import (
    PaymentAgreement,
    PaymentAllocation,
    PaymentInstallment,
    PaymentRecord,
    Portfolio,
)


class PaymentModelTests(
    TestCase
):
    def create_portfolio(
        self,
        name="Payment Project",
    ):
        return (
            Portfolio.objects.create(
                name=name,
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

    def create_agreement(
        self,
        *,
        portfolio=None,
        total_amount=(
            Decimal(
                "1000000.00"
            )
        ),
    ):
        return (
            PaymentAgreement
            .objects
            .create(
                portfolio=(
                    portfolio
                    or self
                    .create_portfolio()
                ),
                title=(
                    "Development "
                    "Contract"
                ),
                agreement_type=(
                    PaymentAgreement
                    .AgreementType
                    .PROJECT
                ),
                currency=(
                    PaymentAgreement
                    .Currency.RWF
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

    def create_installment(
        self,
        agreement,
        *,
        sequence=1,
        amount=Decimal(
            "1000000.00"
        ),
    ):
        return (
            PaymentInstallment
            .objects
            .create(
                agreement=(
                    agreement
                ),
                sequence=sequence,
                title=(
                    f"Installment "
                    f"{sequence}"
                ),
                installment_type=(
                    PaymentInstallment
                    .Type.INSTALLMENT
                ),
                amount=amount,
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

    def test_portfolio_with_agreement_is_protected(
        self,
    ):
        portfolio = (
            self.create_portfolio()
        )

        self.create_agreement(
            portfolio=portfolio,
        )

        with self.assertRaises(
            ProtectedError
        ):
            portfolio.delete()

    def test_agreement_requires_positive_total(
        self,
    ):
        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                self.create_agreement(
                    total_amount=(
                        Decimal(
                            "0.00"
                        )
                    ),
                )

    def test_maintenance_requires_end_date(
        self,
    ):
        agreement = (
            PaymentAgreement(
                portfolio=(
                    self
                    .create_portfolio()
                ),
                title=(
                    "Annual "
                    "Maintenance"
                ),
                agreement_type=(
                    PaymentAgreement
                    .AgreementType
                    .MAINTENANCE
                ),
                total_amount=(
                    Decimal(
                        "2400000.00"
                    )
                ),
                agreement_date=date(
                    2026,
                    12,
                    1,
                ),
                start_date=date(
                    2027,
                    1,
                    1,
                ),
            )
        )

        with self.assertRaises(
            ValidationError
        ):
            agreement.full_clean()

    def test_fixed_installment_requires_due_date(
        self,
    ):
        agreement = (
            self.create_agreement()
        )

        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                (
                    PaymentInstallment
                    .objects
                    .create(
                        agreement=(
                            agreement
                        ),
                        sequence=1,
                        title=(
                            "Down "
                            "payment"
                        ),
                        installment_type=(
                            PaymentInstallment
                            .Type
                            .DOWN_PAYMENT
                        ),
                        amount=(
                            Decimal(
                                "1000000.00"
                            )
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
                    )
                )

    def test_milestone_can_have_only_expected_date(
        self,
    ):
        agreement = (
            self.create_agreement()
        )

        installment = (
            PaymentInstallment
            .objects
            .create(
                agreement=agreement,
                sequence=1,
                title=(
                    "Handover "
                    "payment"
                ),
                installment_type=(
                    PaymentInstallment
                    .Type
                    .MILESTONE
                ),
                amount=Decimal(
                    "1000000.00"
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
                due_date=None,
                milestone=(
                    "Project handover"
                ),
            )
        )

        installment.full_clean()

        self.assertIsNone(
            installment.due_date
        )

    def test_payment_currency_must_match_agreement(
        self,
    ):
        agreement = (
            self.create_agreement()
        )

        payment = PaymentRecord(
            agreement=agreement,
            amount=Decimal(
                "500000.00"
            ),
            currency=(
                PaymentAgreement
                .Currency.USD
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            payment.full_clean()

    def test_allocation_must_use_same_agreement(
        self,
    ):
        first = (
            self.create_agreement()
        )

        second = (
            self.create_agreement(
                portfolio=(
                    self.create_portfolio(
                        "Another Project"
                    )
                )
            )
        )

        payment = (
            PaymentRecord
            .objects
            .create(
                agreement=first,
                amount=Decimal(
                    "500000.00"
                ),
                currency=(
                    PaymentAgreement
                    .Currency.RWF
                ),
            )
        )

        installment = (
            self.create_installment(
                second
            )
        )

        allocation = (
            PaymentAllocation(
                payment=payment,
                installment=(
                    installment
                ),
                amount=Decimal(
                    "100000.00"
                ),
            )
        )

        with self.assertRaises(
            ValidationError
        ):
            allocation.full_clean()

    def test_allocations_cannot_exceed_payment_amount(
        self,
    ):
        agreement = (
            self.create_agreement(
                total_amount=(
                    Decimal(
                        "1000000.00"
                    )
                )
            )
        )

        first = (
            self.create_installment(
                agreement,
                sequence=1,
                amount=Decimal(
                    "500000.00"
                ),
            )
        )

        second = (
            PaymentInstallment
            .objects
            .create(
                agreement=agreement,
                sequence=2,
                title=(
                    "Installment 2"
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
                        11,
                        1,
                    )
                ),
                due_date=date(
                    2026,
                    11,
                    1,
                ),
            )
        )

        payment = (
            PaymentRecord
            .objects
            .create(
                agreement=agreement,
                amount=Decimal(
                    "500000.00"
                ),
                currency="RWF",
            )
        )

        PaymentAllocation.objects.create(
            payment=payment,
            installment=first,
            amount=Decimal(
                "400000.00"
            ),
        )

        extra = PaymentAllocation(
            payment=payment,
            installment=second,
            amount=Decimal(
                "200000.00"
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            extra.full_clean()

    def test_voided_payment_requires_a_reason(
        self,
    ):
        payment = PaymentRecord(
            agreement=(
                self
                .create_agreement()
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
        )

        with self.assertRaises(
            ValidationError
        ):
            payment.full_clean()