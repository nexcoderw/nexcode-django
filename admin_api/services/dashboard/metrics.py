"""Headline figures and chart series for the admin dashboard."""

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import Coalesce, TruncMonth, TruncWeek

from home.models import (
    Client,
    Contact,
    PaymentAgreement,
    PaymentInstallment,
    PaymentRecord,
    Portfolio,
    Team,
)

ZERO = Decimal("0.00")

# The cash-flow chart: eight months back, this month, three ahead.
MONTHS_BACK = 8
MONTHS_AHEAD = 3
MESSAGE_WEEKS = 12


def money(value):
    return f"{(value or ZERO):.2f}"


def month_start(day, offset=0):
    """The first day of the month `offset` months from `day`'s month."""
    index = day.year * 12 + day.month - 1 + offset
    return date(index // 12, index % 12 + 1, 1)


def reporting_currencies():
    """Currencies in use, most agreements first; RWF when there are none."""
    rows = (
        PaymentAgreement.objects.values("currency")
        .annotate(total=Count("pk"))
        .order_by("-total", "currency")
    )
    return [row["currency"] for row in rows] or [PaymentAgreement.Currency.RWF]


def collected_between(currency, start, end):
    """Posted payments received from `start` up to, not including, `end`."""
    return (
        PaymentRecord.objects.filter(
            currency=currency,
            status=PaymentRecord.Status.POSTED,
            paid_at__date__gte=start,
            paid_at__date__lt=end,
        ).aggregate(total=Sum("amount"))["total"]
        or ZERO
    )


def cashflow(currency, today):
    """Per month: what installments expected, and what was collected."""
    first = month_start(today, -MONTHS_BACK)
    after = month_start(today, MONTHS_AHEAD + 1)

    expected = dict(
        PaymentInstallment.objects.filter(
            agreement__currency=currency,
            is_waived=False,
        )
        .exclude(agreement__status=PaymentAgreement.Status.CANCELLED)
        .annotate(due=Coalesce("due_date", "expected_due_date"))
        .filter(due__gte=first, due__lt=after)
        .annotate(month=TruncMonth("due"))
        .values("month")
        .annotate(total=Sum("amount"))
        .values_list("month", "total")
    )

    collected = dict(
        PaymentRecord.objects.filter(
            currency=currency,
            status=PaymentRecord.Status.POSTED,
            paid_at__date__gte=first,
            paid_at__date__lt=after,
        )
        .annotate(month=TruncMonth("paid_at"))
        .values("month")
        .annotate(total=Sum("amount"))
        .values_list("month", "total")
    )

    # Keys come back as dates or datetimes depending on the field.
    expected = {_as_date(key): value for key, value in expected.items()}
    collected = {_as_date(key): value for key, value in collected.items()}

    series = []
    for offset in range(-MONTHS_BACK, MONTHS_AHEAD + 1):
        month = month_start(today, offset)
        series.append(
            {
                "month": month.isoformat()[:7],
                "expected": money(expected.get(month)),
                # Future months have nothing collected yet.
                "collected": money(collected.get(month)) if offset <= 0 else None,
            }
        )
    return series


def messages_by_week(today):
    first = today - timedelta(days=today.weekday() + 7 * (MESSAGE_WEEKS - 1))
    counts = {
        _as_date(row["week"]): row["total"]
        for row in Contact.objects.filter(created_at__date__gte=first)
        .annotate(week=TruncWeek("created_at"))
        .values("week")
        .annotate(total=Count("pk"))
    }
    return [
        {
            "week": (first + timedelta(weeks=index)).isoformat(),
            "count": counts.get(first + timedelta(weeks=index), 0),
        }
        for index in range(MESSAGE_WEEKS)
    ]


def breakdowns():
    statuses = dict(
        PaymentAgreement.objects.values("status")
        .annotate(total=Count("pk"))
        .values_list("status", "total")
    )
    categories = dict(
        Portfolio.objects.values("category")
        .annotate(total=Count("pk"))
        .values_list("category", "total")
    )
    return {
        "agreements_by_status": [
            {"status": value, "label": label, "count": statuses.get(value, 0)}
            for value, label in PaymentAgreement.Status.choices
        ],
        "portfolios_by_category": [
            {"category": value, "label": label, "count": categories.get(value, 0)}
            for value, label in Portfolio.Category.choices
        ],
    }


def activity_counts(today):
    month = month_start(today)
    return {
        "active_agreements": PaymentAgreement.objects.filter(
            status=PaymentAgreement.Status.ACTIVE
        ).count(),
        "agreements": PaymentAgreement.objects.count(),
        "unanswered_messages": Contact.objects.filter(replied_at__isnull=True).count(),
        "messages_this_month": Contact.objects.filter(
            created_at__date__gte=month
        ).count(),
        "clients": Client.objects.count(),
        "published_portfolios": Portfolio.objects.filter(
            status=Portfolio.Status.PUBLISHED
        ).count(),
        "portfolios": Portfolio.objects.count(),
        "team_members": Team.objects.count(),
    }


def _as_date(value):
    return value.date() if hasattr(value, "date") and callable(value.date) else value
