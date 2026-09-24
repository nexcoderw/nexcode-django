"""Reminders the admin schedules for a chosen calendar date."""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase

from admin_api.constants import NEXCODE_ADMIN_GROUP_NAME
from home.models import (
    PaymentAgreement,
    PaymentAllocation,
    PaymentInstallment,
    PaymentNotification,
    PaymentRecord,
    PaymentReminderRule,
    Portfolio,
)
from home.services.payment.reminder import process_payment_reminders


class SetDateReminderTests(TestCase):
    def setUp(self):
        group = Group.objects.create(name=NEXCODE_ADMIN_GROUP_NAME)
        self.user = get_user_model().objects.create_user(
            username="finance@nexcode.africa",
            email="finance@nexcode.africa",
            password="Password123!",
        )
        self.user.groups.add(group)

        portfolio = Portfolio.objects.create(
            name="Talent Match Platform",
            category=Portfolio.Category.WEB_APPLICATION,
            project_type=Portfolio.ProjectType.CLIENT_PROJECT,
        )
        self.agreement = PaymentAgreement.objects.create(
            portfolio=portfolio,
            title="Maintenance Contract",
            agreement_type=PaymentAgreement.AgreementType.MAINTENANCE,
            currency="RWF",
            total_amount=Decimal("450000.00"),
            agreement_date=date(2025, 12, 18),
            start_date=date(2025, 12, 18),
            end_date=date(2026, 12, 18),
            status=PaymentAgreement.Status.ACTIVE,
        )
        self.october, self.november, self.december = [
            PaymentInstallment.objects.create(
                agreement=self.agreement,
                sequence=sequence,
                title=f"Maintenance {sequence}",
                installment_type=PaymentInstallment.Type.MAINTENANCE,
                amount=Decimal("150000.00"),
                due_type=PaymentInstallment.DueType.FIXED_DATE,
                expected_due_date=due,
                due_date=due,
            )
            for sequence, due in (
                (1, date(2026, 10, 1)),
                (2, date(2026, 11, 1)),
                (3, date(2026, 12, 1)),
            )
        ]

    def dated_rule(self, remind_on, event=PaymentReminderRule.Event.INSTALLMENT_DUE):
        return PaymentReminderRule.objects.create(
            agreement=self.agreement,
            event=event,
            timing=PaymentReminderRule.Timing.DATE,
            remind_on=remind_on,
        )

    def process(self, on_date):
        return process_payment_reminders(recipients=[self.user], on_date=on_date)

    def pay(self, installment):
        payment = PaymentRecord.objects.create(
            agreement=self.agreement,
            amount=installment.amount,
            currency="RWF",
        )
        PaymentAllocation.objects.create(
            payment=payment, installment=installment, amount=installment.amount
        )

    def test_fires_only_on_the_chosen_date(self):
        self.dated_rule(date(2026, 9, 28))

        for other_day in (date(2026, 9, 27), date(2026, 9, 29)):
            self.assertEqual(self.process(other_day).created, 0)

        self.assertEqual(self.process(date(2026, 9, 28)).created, 1)

    def test_reminds_about_the_earliest_open_installment_only(self):
        self.dated_rule(date(2026, 9, 28))

        self.process(date(2026, 9, 28))

        notification = PaymentNotification.objects.get()
        self.assertEqual(notification.installment, self.october)
        self.assertEqual(notification.trigger_date, date(2026, 9, 28))
        self.assertEqual(notification.target_date, date(2026, 10, 1))
        self.assertEqual(notification.title, "Payment reminder")
        self.assertIn("2026-10-01", notification.message)

    def test_skips_installments_already_paid(self):
        self.pay(self.october)
        self.dated_rule(date(2026, 10, 25))

        self.process(date(2026, 10, 25))

        self.assertEqual(
            PaymentNotification.objects.get().installment, self.november
        )

    def test_nothing_is_sent_once_everything_is_paid(self):
        for installment in (self.october, self.november, self.december):
            self.pay(installment)
        self.dated_rule(date(2026, 9, 28))

        self.assertEqual(self.process(date(2026, 9, 28)).created, 0)

    def test_running_twice_on_the_day_sends_once(self):
        self.dated_rule(date(2026, 9, 28))

        self.process(date(2026, 9, 28))
        second = self.process(date(2026, 9, 28))

        self.assertEqual(second.created, 0)
        self.assertEqual(PaymentNotification.objects.count(), 1)

    def test_agreement_expiry_on_a_set_date(self):
        self.dated_rule(
            date(2026, 12, 1), event=PaymentReminderRule.Event.AGREEMENT_EXPIRY
        )

        self.process(date(2026, 12, 1))

        notification = PaymentNotification.objects.get()
        self.assertEqual(notification.title, "Agreement expiry reminder")
        self.assertEqual(notification.target_date, date(2026, 12, 18))

    def test_relative_rules_are_unaffected(self):
        PaymentReminderRule.objects.create(
            agreement=self.agreement,
            event=PaymentReminderRule.Event.INSTALLMENT_DUE,
            timing=PaymentReminderRule.Timing.BEFORE,
            days=3,
        )

        # Three days before each due date, one reminder each.
        self.assertEqual(self.process(date(2026, 9, 28)).created, 1)
        self.assertEqual(self.process(date(2026, 10, 29)).created, 1)

    def test_rule_validation(self):
        cases = (
            # A set date is required, and takes no offset.
            {"timing": "date", "remind_on": None},
            {"timing": "date", "remind_on": date(2026, 9, 28), "days": 3},
            # Relative timings take no date.
            {"timing": "before", "days": 3, "remind_on": date(2026, 9, 28)},
        )

        for fields in cases:
            with self.subTest(fields=fields):
                rule = PaymentReminderRule(
                    agreement=self.agreement,
                    event=PaymentReminderRule.Event.INSTALLMENT_DUE,
                    **fields,
                )

                with self.assertRaises(ValidationError):
                    rule.full_clean()

    def test_one_rule_per_date_and_channel(self):
        self.dated_rule(date(2026, 9, 28))

        duplicate = PaymentReminderRule(
            agreement=self.agreement,
            event=PaymentReminderRule.Event.INSTALLMENT_DUE,
            timing=PaymentReminderRule.Timing.DATE,
            remind_on=date(2026, 9, 28),
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

        # Another date is a separate reminder.
        self.dated_rule(date(2026, 10, 28))
        self.assertEqual(PaymentReminderRule.objects.count(), 2)
