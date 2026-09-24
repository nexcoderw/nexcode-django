"""The admin dashboard: one read that answers "how is the business doing?"."""

from datetime import timedelta

from home.models import PaymentRecord

from admin_api.services.dashboard.alerts import (
    attention,
    balances,
    installment_positions,
)
from admin_api.services.dashboard.metrics import (
    activity_counts,
    breakdowns,
    cashflow,
    collected_between,
    messages_by_week,
    money,
    month_start,
    reporting_currencies,
)

RECENT_PAYMENTS = 5
EXPECTED_WINDOW_DAYS = 30


class DashboardCurrencyError(ValueError):
    pass


def build_overview(today, currency=None):
    """
    Everything the dashboard shows. Money figures are in one reporting
    currency (the most used unless one is asked for); alerts and counts
    cover every agreement.
    """
    currencies = reporting_currencies()

    if currency is None:
        currency = currencies[0]
    elif currency not in currencies:
        raise DashboardCurrencyError("No agreements use this currency.")

    positions = installment_positions(today)
    outstanding, overdue, overdue_count = balances(currency, positions)

    this_month = month_start(today)

    return {
        "currency": currency,
        "currencies": currencies,
        "today": today.isoformat(),
        "money": {
            "collected_this_month": money(
                collected_between(currency, this_month, month_start(today, 1))
            ),
            "collected_last_month": money(
                collected_between(currency, month_start(today, -1), this_month)
            ),
            "collected_this_year": money(
                collected_between(
                    currency, this_month.replace(month=1), month_start(today, 1)
                )
            ),
            "outstanding": money(outstanding),
            "overdue": money(overdue),
            "overdue_count": overdue_count,
            "expected_next_30_days": money(
                _expected_soon(currency, today, positions)
            ),
        },
        "counts": activity_counts(today),
        "cashflow": cashflow(currency, today),
        "messages_by_week": messages_by_week(today),
        **breakdowns(),
        "alerts": attention(today, positions),
        "recent_payments": _recent_payments(currency),
    }


def _expected_soon(currency, today, positions):
    """Still owed on installments falling due in the next 30 days."""
    horizon = today + timedelta(days=EXPECTED_WINDOW_DAYS)
    total = 0
    for installment, status in positions:
        due = status.effective_due_date
        if (
            installment.agreement.currency == currency
            and due is not None
            and today <= due <= horizon
        ):
            total += status.outstanding_amount
    return total


def _recent_payments(currency):
    payments = (
        PaymentRecord.objects.filter(
            currency=currency, status=PaymentRecord.Status.POSTED
        )
        .select_related("agreement", "agreement__portfolio")
        .order_by("-paid_at", "-pk")[:RECENT_PAYMENTS]
    )
    return [
        {
            "id": payment.pk,
            "agreement_id": payment.agreement_id,
            "agreement_title": payment.agreement.title,
            "portfolio_name": payment.agreement.portfolio.name,
            "amount": money(payment.amount),
            "paid_at": payment.paid_at.isoformat(),
            "payment_method": payment.payment_method,
        }
        for payment in payments
    ]
