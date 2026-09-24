"""What needs attention: money due soon, overdue, and contracts ending."""

from datetime import timedelta
from decimal import Decimal

from django.db.models import DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce

from home.models import PaymentAgreement, PaymentInstallment, PaymentRecord
from home.services.payment.status import TimingState, get_installment_status

ZERO = Decimal("0.00")

DUE_SOON_DAYS = 7
ENDING_SOON_DAYS = 30
ALERT_LIMIT = 10


def open_installments():
    """Unpaid installments on live agreements, with what has been paid."""
    return (
        PaymentInstallment.objects.filter(
            is_waived=False,
            agreement__status=PaymentAgreement.Status.ACTIVE,
        )
        .select_related("agreement", "agreement__portfolio")
        .annotate(
            paid=Coalesce(
                Sum(
                    "allocations__amount",
                    filter=Q(
                        allocations__payment__status=PaymentRecord.Status.POSTED
                    ),
                ),
                Value(ZERO),
                output_field=DecimalField(max_digits=18, decimal_places=2),
            )
        )
    )


def installment_positions(today):
    """Each open installment with its outstanding amount and timing."""
    positions = []
    for installment in open_installments():
        status = get_installment_status(
            installment, on_date=today, paid_amount=installment.paid
        )
        if status.outstanding_amount > ZERO:
            positions.append((installment, status))
    return positions


def attention(today, positions):
    """The alert lists, soonest and most overdue first."""
    horizon = today + timedelta(days=DUE_SOON_DAYS)

    due_soon = []
    overdue = []
    for installment, status in positions:
        due = status.effective_due_date
        if due is None:
            continue
        # Past due, whether still inside its grace period or beyond it.
        if status.timing_state in (TimingState.OVERDUE, TimingState.GRACE_PERIOD):
            overdue.append(_alert(installment, status, (today - due).days))
        elif today <= due <= horizon:
            due_soon.append(_alert(installment, status, (due - today).days))

    due_soon.sort(key=lambda item: item["due_date"])
    overdue.sort(key=lambda item: item["due_date"])

    return {
        "due_soon": due_soon[:ALERT_LIMIT],
        "overdue": overdue[:ALERT_LIMIT],
        "ending_soon": _ending_soon(today),
    }


def balances(currency, positions):
    """Outstanding and overdue totals for one currency."""
    outstanding = ZERO
    overdue = ZERO
    overdue_count = 0
    for installment, status in positions:
        if installment.agreement.currency != currency:
            continue
        outstanding += status.outstanding_amount
        if status.timing_state == TimingState.OVERDUE:
            overdue += status.outstanding_amount
            overdue_count += 1
    return outstanding, overdue, overdue_count


def _alert(installment, status, days):
    agreement = installment.agreement
    return {
        "installment_id": installment.pk,
        "agreement_id": agreement.pk,
        "agreement_title": agreement.title,
        "portfolio_name": agreement.portfolio.name,
        "title": installment.title,
        "due_date": status.effective_due_date.isoformat(),
        "days": days,
        "outstanding": f"{status.outstanding_amount:.2f}",
        "currency": agreement.currency,
        "in_grace": status.timing_state == TimingState.GRACE_PERIOD,
    }


def _ending_soon(today):
    agreements = (
        PaymentAgreement.objects.filter(
            status=PaymentAgreement.Status.ACTIVE,
            end_date__gte=today,
            end_date__lte=today + timedelta(days=ENDING_SOON_DAYS),
        )
        .select_related("portfolio")
        .order_by("end_date", "pk")[:ALERT_LIMIT]
    )
    return [
        {
            "agreement_id": agreement.pk,
            "agreement_title": agreement.title,
            "portfolio_name": agreement.portfolio.name,
            "end_date": agreement.end_date.isoformat(),
            "days": (agreement.end_date - today).days,
        }
        for agreement in agreements
    ]
