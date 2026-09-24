from datetime import date
from decimal import Decimal

from django.contrib.auth import (
    get_user_model,
)
from django.contrib.auth.models import (
    Group,
)
from django.test import TestCase

from admin_api.constants import (
    NEXCODE_ADMIN_GROUP_NAME,
)
from home.models import (
    PaymentAgreement,
    PaymentAllocation,
    PaymentInstallment,
    PaymentNotification,
    PaymentRecord,
    PaymentReminderRule,
    Portfolio,
)
from home.services.payment.reminder import (
    process_payment_reminders,
)


class PaymentReminderTests(
    TestCase
):
    def setUp(self):
        User = get_user_model()

        group = Group.objects.create(
            name=(
                NEXCODE_ADMIN_GROUP_NAME
            )
        )

        self.user = (
            User.objects.create_user(
                username=(
                    "finance@nexcode.africa"
                ),
                email=(
                    "finance@nexcode.africa"
                ),
                password=(
                    "Password123!"
                ),
            )
        )

        self.user.groups.add(
            group
        )

        self.portfolio = (
            Portfolio.objects.create(
                name="Client Portal",
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
                    "Development Contract"
                ),
                agreement_type=(
                    PaymentAgreement
                    .AgreementType
                    .PROJECT
                ),
                currency="RWF",
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
                    "October payment"
                ),
                amount=Decimal(
                    "1000000.00"
                ),
                due_type=(
                    PaymentInstallment
                    .DueType
                    .FIXED_DATE
                ),
                expected_due_date=date(
                    2026,
                    10,
                    1,
                ),
                due_date=date(
                    2026,
                    10,
                    1,
                ),
            )
        )

    def test_due_reminder_is_generated(
        self,
    ):
        PaymentReminderRule.objects.create(
            agreement=(
                self.agreement
            ),
            event=(
                PaymentReminderRule
                .Event.INSTALLMENT_DUE
            ),
            timing=(
                PaymentReminderRule
                .Timing.BEFORE
            ),
            days=7,
            channel=(
                PaymentReminderRule
                .Channel.IN_APP
            ),
        )

        result = (
            process_payment_reminders(
                recipients=[
                    self.user
                ],
                on_date=date(
                    2026,
                    9,
                    24,
                ),
            )
        )

        self.assertEqual(
            result.created,
            1,
        )

        notification = (
            PaymentNotification
            .objects
            .get()
        )

        self.assertEqual(
            notification.status,
            (
                PaymentNotification
                .Status.SENT
            ),
        )

        self.assertEqual(
            notification
            .installment_id,
            self.installment.pk,
        )

    def test_processor_is_idempotent(
        self,
    ):
        PaymentReminderRule.objects.create(
            agreement=(
                self.agreement
            ),
            event=(
                PaymentReminderRule
                .Event.INSTALLMENT_DUE
            ),
            timing=(
                PaymentReminderRule
                .Timing.ON
            ),
            days=0,
        )

        for _ in range(2):
            process_payment_reminders(
                recipients=[
                    self.user
                ],
                on_date=date(
                    2026,
                    10,
                    1,
                ),
            )

        self.assertEqual(
            PaymentNotification
            .objects
            .count(),
            1,
        )

    def test_paid_installment_is_skipped(
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
                    "1000000.00"
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
                    "1000000.00"
                ),
            )
        )

        PaymentReminderRule.objects.create(
            agreement=(
                self.agreement
            ),
            event=(
                PaymentReminderRule
                .Event.INSTALLMENT_DUE
            ),
            timing=(
                PaymentReminderRule
                .Timing.ON
            ),
            days=0,
        )

        process_payment_reminders(
            recipients=[
                self.user
            ],
            on_date=date(
                2026,
                10,
                1,
            ),
        )

        self.assertFalse(
            PaymentNotification
            .objects
            .exists()
        )

    def test_unconfirmed_milestone_uses_expected_date(
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
                    "Handover payment"
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
                expected_due_date=date(
                    2026,
                    12,
                    15,
                ),
                due_date=None,
                milestone=(
                    "Project handover"
                ),
            )
        )

        PaymentReminderRule.objects.create(
            agreement=(
                self.agreement
            ),
            event=(
                PaymentReminderRule
                .Event
                .MILESTONE_EXPECTED
            ),
            timing=(
                PaymentReminderRule
                .Timing.BEFORE
            ),
            days=7,
        )

        process_payment_reminders(
            recipients=[
                self.user
            ],
            on_date=date(
                2026,
                12,
                8,
            ),
        )

        notification = (
            PaymentNotification
            .objects
            .get()
        )

        self.assertEqual(
            notification
            .installment_id,
            milestone.pk,
        )

    def test_completed_agreement_is_ignored(
        self,
    ):
        self.agreement.status = (
            PaymentAgreement
            .Status.COMPLETED
        )

        self.agreement.save(
            update_fields=(
                "status",
            )
        )

        PaymentReminderRule.objects.create(
            agreement=(
                self.agreement
            ),
            event=(
                PaymentReminderRule
                .Event.INSTALLMENT_DUE
            ),
            timing=(
                PaymentReminderRule
                .Timing.ON
            ),
            days=0,
        )

        process_payment_reminders(
            recipients=[
                self.user
            ],
            on_date=date(
                2026,
                10,
                1,
            ),
        )

        self.assertFalse(
            PaymentNotification
            .objects
            .exists()
        )