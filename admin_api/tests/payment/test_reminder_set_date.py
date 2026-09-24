from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from admin_api.tests.payment.base import PaymentApiTestCase
from home.models import PaymentReminderRule


class SetDateReminderApiTests(PaymentApiTestCase):
    def setUp(self):
        super().setUp()
        self.login_admin()
        self.agreement = self.create_agreement()
        self.today = timezone.localdate()

    def add_url(self):
        return reverse(
            "admin_api:payment:reminder_rule_add",
            kwargs={"agreement_id": self.agreement.pk},
        )

    def update_url(self, rule):
        return reverse(
            "admin_api:payment:reminder_rule_update",
            kwargs={"rule_id": rule.pk},
        )

    def add(self, **payload):
        return self.post_json(
            self.add_url(),
            {"event": "installment_due", "channel": "in_app", **payload},
        )

    def test_admin_can_create_a_reminder_on_a_set_date(self):
        remind_on = self.today + timedelta(days=5)

        response = self.add(timing="date", remind_on=remind_on.isoformat())

        self.assertEqual(response.status_code, 201)

        rule = PaymentReminderRule.objects.get()
        self.assertEqual(rule.timing, "date")
        self.assertEqual(rule.remind_on, remind_on)
        self.assertEqual(rule.days, 0)

        data = response.json()["data"]["rule"]
        self.assertEqual(data["remind_on"], remind_on.isoformat())
        self.assertEqual(data["timing"], "date")

    def test_any_offset_sent_with_a_set_date_is_dropped(self):
        response = self.add(
            timing="date",
            remind_on=(self.today + timedelta(days=5)).isoformat(),
            days=7,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(PaymentReminderRule.objects.get().days, 0)

    def test_set_date_is_required(self):
        response = self.add(timing="date")

        self.assertEqual(response.status_code, 400)
        self.assertIn("remind_on", response.json()["errors"])
        self.assertFalse(PaymentReminderRule.objects.exists())

    def test_a_past_date_is_rejected(self):
        response = self.add(
            timing="date",
            remind_on=(self.today - timedelta(days=1)).isoformat(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("remind_on", response.json()["errors"])

    def test_today_is_allowed(self):
        response = self.add(timing="date", remind_on=self.today.isoformat())

        self.assertEqual(response.status_code, 201)

    def test_relative_rules_still_work_and_carry_no_date(self):
        response = self.add(timing="before", days=3)

        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.json()["data"]["rule"]["remind_on"])

    def test_the_date_can_be_moved(self):
        rule = PaymentReminderRule.objects.create(
            agreement=self.agreement,
            event="installment_due",
            timing="date",
            remind_on=self.today + timedelta(days=5),
        )
        moved = self.today + timedelta(days=9)

        response = self.patch_json(
            self.update_url(rule), {"remind_on": moved.isoformat()}
        )

        self.assertEqual(response.status_code, 200)
        rule.refresh_from_db()
        self.assertEqual(rule.remind_on, moved)

    def test_switching_to_a_relative_timing_clears_the_date(self):
        rule = PaymentReminderRule.objects.create(
            agreement=self.agreement,
            event="installment_due",
            timing="date",
            remind_on=self.today + timedelta(days=5),
        )

        response = self.patch_json(
            self.update_url(rule), {"timing": "before", "days": 3}
        )

        self.assertEqual(response.status_code, 200)
        rule.refresh_from_db()
        self.assertEqual(rule.timing, "before")
        self.assertIsNone(rule.remind_on)

    def test_switching_to_a_set_date_requires_the_date(self):
        rule = PaymentReminderRule.objects.create(
            agreement=self.agreement,
            event="installment_due",
            timing="before",
            days=3,
        )

        response = self.patch_json(self.update_url(rule), {"timing": "date"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("remind_on", response.json()["errors"])
