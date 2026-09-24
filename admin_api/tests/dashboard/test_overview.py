from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from admin_api.tests.payment.base import PaymentApiTestCase
from home.models import (
    Contact,
    PaymentAgreement,
    PaymentAllocation,
    PaymentRecord,
)


class DashboardOverviewTests(PaymentApiTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("admin_api:dashboard:overview")
        self.today = timezone.localdate()

    def overview(self, **params):
        self.login_admin()
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()["data"]

    def installment(self, agreement, sequence, days_from_today, amount="100000.00"):
        due = self.today + timedelta(days=days_from_today)
        return self.create_installment(
            agreement,
            sequence=sequence,
            title=f"Installment {sequence}",
            amount=Decimal(amount),
            expected_due_date=due,
            due_date=due,
        )

    def pay(self, agreement, installment, amount="100000.00", days_ago=0):
        paid_on = self.today - timedelta(days=days_ago)
        payment = PaymentRecord.objects.create(
            agreement=agreement,
            amount=Decimal(amount),
            currency=agreement.currency,
            paid_at=timezone.make_aware(datetime.combine(paid_on, time(12))),
        )
        PaymentAllocation.objects.create(
            payment=payment, installment=installment, amount=Decimal(amount)
        )
        return payment

    def test_requires_an_administrator(self):
        self.assertEqual(self.client.get(self.url).status_code, 401)

        regular = get_user_model().objects.create_user(
            username="user@nexcode.africa",
            email="user@nexcode.africa",
            password="Password123!",
        )
        self.client.force_login(regular)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_empty_workspace_still_answers(self):
        data = self.overview()

        self.assertEqual(data["currency"], "RWF")
        self.assertEqual(data["money"]["outstanding"], "0.00")
        self.assertEqual(len(data["cashflow"]), 12)
        self.assertEqual(len(data["messages_by_week"]), 12)
        self.assertEqual(
            data["alerts"], {"due_soon": [], "overdue": [], "ending_soon": []}
        )

    def test_alerts_installments_due_within_a_week(self):
        agreement = self.create_agreement(total_amount=Decimal("400000.00"))
        soon = self.installment(agreement, 1, 3)
        self.installment(agreement, 2, 10)  # beyond the week
        paid = self.installment(agreement, 3, 2)
        self.pay(agreement, paid)

        due_soon = self.overview()["alerts"]["due_soon"]

        self.assertEqual([item["installment_id"] for item in due_soon], [soon.pk])
        self.assertEqual(due_soon[0]["days"], 3)
        self.assertEqual(due_soon[0]["outstanding"], "100000.00")
        self.assertEqual(due_soon[0]["currency"], "RWF")

    def test_partly_paid_installments_show_what_is_left(self):
        agreement = self.create_agreement(total_amount=Decimal("100000.00"))
        installment = self.installment(agreement, 1, 4)
        self.pay(agreement, installment, amount="40000.00")

        due_soon = self.overview()["alerts"]["due_soon"]

        self.assertEqual(due_soon[0]["outstanding"], "60000.00")

    def test_overdue_installments_are_listed_and_totalled(self):
        agreement = self.create_agreement(total_amount=Decimal("300000.00"))
        self.installment(agreement, 1, -20)
        self.installment(agreement, 2, 3)

        data = self.overview()

        overdue = data["alerts"]["overdue"]
        self.assertEqual(len(overdue), 1)
        self.assertEqual(overdue[0]["days"], 20)
        self.assertEqual(data["money"]["overdue"], "100000.00")
        self.assertEqual(data["money"]["overdue_count"], 1)
        self.assertEqual(data["money"]["outstanding"], "200000.00")

    def test_grace_period_is_listed_but_not_yet_counted_overdue(self):
        agreement = self.create_agreement(total_amount=Decimal("100000.00"))
        installment = self.installment(agreement, 1, -2)
        installment.grace_period_days = 5
        installment.save(update_fields=["grace_period_days"])

        data = self.overview()

        self.assertTrue(data["alerts"]["overdue"][0]["in_grace"])
        self.assertEqual(data["money"]["overdue"], "0.00")

    def test_cancelled_and_draft_agreements_raise_no_alerts(self):
        for status in (PaymentAgreement.Status.CANCELLED, PaymentAgreement.Status.DRAFT):
            agreement = self.create_agreement(status=status)
            self.installment(agreement, 1, 2)

        self.assertEqual(self.overview()["alerts"]["due_soon"], [])

    def test_collected_money_and_cashflow(self):
        agreement = self.create_agreement(total_amount=Decimal("200000.00"))
        first = self.installment(agreement, 1, 0)
        self.installment(agreement, 2, 45)
        self.pay(agreement, first)

        data = self.overview()

        self.assertEqual(data["money"]["collected_this_month"], "100000.00")
        self.assertEqual(data["money"]["collected_this_year"], "100000.00")
        self.assertEqual(data["recent_payments"][0]["amount"], "100000.00")

        this_month = self.today.isoformat()[:7]
        current = next(row for row in data["cashflow"] if row["month"] == this_month)
        self.assertEqual(current["collected"], "100000.00")
        self.assertEqual(current["expected"], "100000.00")

        # Months ahead have expectations but nothing collected yet.
        self.assertIsNone(data["cashflow"][-1]["collected"])

    def test_money_is_reported_in_one_currency(self):
        rwf = self.create_agreement(total_amount=Decimal("100000.00"))
        usd = self.create_agreement(currency="USD", total_amount=Decimal("500.00"))
        self.create_agreement(currency="USD", total_amount=Decimal("500.00"))
        self.installment(rwf, 1, 2)
        self.installment(usd, 1, 2, amount="500.00")

        # USD has the most agreements, so it is the default.
        data = self.overview()
        self.assertEqual(data["currency"], "USD")
        self.assertEqual(data["currencies"], ["USD", "RWF"])
        self.assertEqual(data["money"]["outstanding"], "500.00")

        # Alerts still cover every currency.
        self.assertEqual(len(data["alerts"]["due_soon"]), 2)

        self.assertEqual(self.overview(currency="RWF")["money"]["outstanding"], "100000.00")

    def test_unknown_currency_is_rejected(self):
        self.login_admin()

        response = self.client.get(self.url, {"currency": "BTC"})

        self.assertEqual(response.status_code, 400)

    def test_agreements_ending_within_a_month(self):
        self.create_agreement(end_date=self.today + timedelta(days=20))
        self.create_agreement(end_date=self.today + timedelta(days=60))

        ending = self.overview()["alerts"]["ending_soon"]

        self.assertEqual([item["days"] for item in ending], [20])

    def test_message_counts(self):
        Contact.objects.create(
            name="Jane", email="jane@example.com", subject="Hi", message="Hello"
        )

        data = self.overview()

        self.assertEqual(data["counts"]["unanswered_messages"], 1)
        self.assertEqual(data["messages_by_week"][-1]["count"], 1)
