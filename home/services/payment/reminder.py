import hashlib
import logging

from dataclasses import dataclass
from datetime import (
    date,
    timedelta,
)
from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import (
    DecimalField,
    Q,
    Sum,
    Value,
)
from django.db.models.functions import (
    Coalesce,
)
from django.utils import timezone

from home.models import (
    PaymentInstallment,
    PaymentNotification,
    PaymentRecord,
    PaymentReminderRule,
)


logger = logging.getLogger(
    __name__
)

ZERO = Decimal(
    "0.00"
)


@dataclass(
    frozen=True,
    slots=True,
)
class ReminderProcessResult:
    created: int = 0
    sent: int = 0
    failed: int = 0
    skipped: int = 0


@dataclass(
    frozen=True,
    slots=True,
)
class ReminderTarget:
    kind: str
    target_id: int
    target_date: date
    installment: PaymentInstallment | None
    outstanding_amount: Decimal | None


def process_payment_reminders(
    *,
    recipients,
    on_date:
        date | None = None,
) -> ReminderProcessResult:
    """
    Generate reminders due on one calendar date.

    The dedupe key makes this operation safe to execute repeatedly for
    the same day.
    """

    process_date = (
        on_date
        or timezone.localdate()
    )

    recipients = list(
        recipients
    )

    if not recipients:
        return (
            ReminderProcessResult()
        )

    rules = (
        PaymentReminderRule
        .objects
        .filter(
            is_enabled=True,
            agreement__status="active",
        )
        .select_related(
            "agreement",
            "agreement__portfolio",
        )
    )

    created = 0
    sent = 0
    failed = 0
    skipped = 0

    for rule in rules:
        dated = (
            rule.timing
            == (
                PaymentReminderRule
                .Timing.DATE
            )
        )

        # A set-date rule has nothing to do on any other day, so its
        # targets are not even loaded.
        if (
            dated
            and rule.remind_on
            != process_date
        ):
            continue

        targets = (
            _targets_for_rule(
                rule
            )
        )

        if dated:
            # One reminder on the chosen day, about the earliest item
            # still open, rather than one per outstanding installment.
            targets = sorted(
                targets,
                key=lambda target: (
                    target.target_date
                ),
            )[:1]

        for target in targets:
            trigger_date = (
                _get_trigger_date(
                    target.target_date,
                    rule,
                )
            )

            if (
                trigger_date
                != process_date
            ):
                continue

            for recipient in recipients:
                notification, was_created = (
                    _create_notification(
                        rule=rule,
                        target=target,
                        recipient=recipient,
                        trigger_date=(
                            trigger_date
                        ),
                    )
                )

                if not was_created:
                    skipped += 1
                    continue

                created += 1

                notification = (
                    deliver_payment_notification(
                        notification
                    )
                )

                if (
                    notification.status
                    == (
                        PaymentNotification
                        .Status.SENT
                    )
                ):
                    sent += 1
                else:
                    failed += 1

    return ReminderProcessResult(
        created=created,
        sent=sent,
        failed=failed,
        skipped=skipped,
    )


def retry_failed_notifications(
    *,
    notifications,
) -> ReminderProcessResult:
    sent = 0
    failed = 0
    skipped = 0

    for notification in (
        notifications
    ):
        if (
            notification.status
            != (
                PaymentNotification
                .Status.FAILED
            )
        ):
            skipped += 1
            continue

        result = (
            deliver_payment_notification(
                notification
            )
        )

        if (
            result.status
            == (
                PaymentNotification
                .Status.SENT
            )
        ):
            sent += 1
        else:
            failed += 1

    return ReminderProcessResult(
        sent=sent,
        failed=failed,
        skipped=skipped,
    )


def deliver_payment_notification(
    notification,
):
    """
    Deliver one notification.

    In-app notifications are considered delivered once persisted.
    Email failures remain stored and can be retried explicitly.
    """

    notification = (
        PaymentNotification
        .objects
        .select_related(
            "recipient_user"
        )
        .get(
            pk=notification.pk
        )
    )

    if (
        notification.status
        == (
            PaymentNotification
            .Status.SENT
        )
    ):
        return notification

    notification.attempt_count += 1
    notification.last_attempt_at = (
        timezone.now()
    )
    notification.failure_reason = ""

    if (
        notification.channel
        == (
            PaymentReminderRule
            .Channel.IN_APP
        )
    ):
        notification.status = (
            PaymentNotification
            .Status.SENT
        )

        notification.sent_at = (
            timezone.now()
        )

        notification.save(
            update_fields=(
                "attempt_count",
                "last_attempt_at",
                "failure_reason",
                "status",
                "sent_at",
            )
        )

        return notification

    recipient = (
        notification
        .recipient_user
    )

    recipient_email = (
        getattr(
            recipient,
            "email",
            "",
        )
        or ""
    ).strip()

    if not recipient_email:
        return _mark_failed(
            notification,
            (
                "Recipient has no "
                "email address."
            ),
        )

    try:
        send_mail(
            subject=(
                notification.title
            ),
            message=(
                notification.message
            ),
            from_email=(
                settings
                .DEFAULT_FROM_EMAIL
            ),
            recipient_list=[
                recipient_email
            ],
            fail_silently=False,
        )
    except Exception:
        # Email backends are an external I/O boundary. Keep technical
        # details in server logs rather than exposing them to the API.
        logger.exception(
            (
                "Payment reminder "
                "email delivery failed."
            ),
            extra={
                "notification_id":
                    notification.pk,
            },
        )

        return _mark_failed(
            notification,
            "Email delivery failed.",
        )

    notification.status = (
        PaymentNotification
        .Status.SENT
    )

    notification.sent_at = (
        timezone.now()
    )

    notification.save(
        update_fields=(
            "attempt_count",
            "last_attempt_at",
            "failure_reason",
            "status",
            "sent_at",
        )
    )

    return notification


def _targets_for_rule(
    rule,
):
    if (
        rule.event
        == (
            PaymentReminderRule
            .Event.AGREEMENT_EXPIRY
        )
    ):
        if not rule.agreement.end_date:
            return []

        return [
            ReminderTarget(
                kind="agreement",
                target_id=(
                    rule.agreement_id
                ),
                target_date=(
                    rule.agreement
                    .end_date
                ),
                installment=None,
                outstanding_amount=None,
            ),
        ]

    installments = (
        _installment_queryset(
            rule
        )
    )

    targets = []

    for installment in (
        installments
    ):
        paid_amount = (
            installment
            .posted_paid_amount
        )

        if (
            paid_amount
            >= installment.amount
        ):
            continue

        outstanding = (
            installment.amount
            - paid_amount
        )

        if (
            rule.event
            == (
                PaymentReminderRule
                .Event
                .INSTALLMENT_DUE
            )
        ):
            if not installment.due_date:
                continue

            target_date = (
                installment.due_date
            )

        else:
            # Forecast reminders are intentionally limited to
            # unconfirmed milestones. A confirmed milestone moves to
            # the normal due-date reminder flow.
            if (
                installment.due_type
                != (
                    PaymentInstallment
                    .DueType.MILESTONE
                )
                or installment
                .due_date is not None
            ):
                continue

            target_date = (
                installment
                .expected_due_date
            )

        targets.append(
            ReminderTarget(
                kind="installment",
                target_id=(
                    installment.pk
                ),
                target_date=(
                    target_date
                ),
                installment=(
                    installment
                ),
                outstanding_amount=(
                    outstanding
                ),
            )
        )

    return targets


def _installment_queryset(
    rule,
):
    return (
        PaymentInstallment
        .objects
        .filter(
            agreement=(
                rule.agreement
            ),
            is_waived=False,
        )
        .annotate(
            posted_paid_amount=(
                Coalesce(
                    Sum(
                        "allocations__amount",
                        filter=Q(
                            allocations__payment__status=(
                                PaymentRecord
                                .Status.POSTED
                            ),
                        ),
                    ),
                    Value(
                        ZERO
                    ),
                    output_field=(
                        DecimalField(
                            max_digits=18,
                            decimal_places=2,
                        )
                    ),
                )
            )
        )
    )


def _get_trigger_date(
    target_date,
    rule,
):
    if (
        rule.timing
        == (
            PaymentReminderRule
            .Timing.DATE
        )
    ):
        return rule.remind_on

    offset = timedelta(
        days=rule.days
    )

    if (
        rule.timing
        == (
            PaymentReminderRule
            .Timing.BEFORE
        )
    ):
        return (
            target_date
            - offset
        )

    if (
        rule.timing
        == (
            PaymentReminderRule
            .Timing.AFTER
        )
    ):
        return (
            target_date
            + offset
        )

    return target_date


@transaction.atomic
def _create_notification(
    *,
    rule,
    target,
    recipient,
    trigger_date,
):
    dedupe_key = (
        _dedupe_key(
            rule=rule,
            target=target,
            recipient=recipient,
            trigger_date=(
                trigger_date
            ),
        )
    )

    title, message = (
        _notification_content(
            rule,
            target,
        )
    )

    return (
        PaymentNotification
        .objects
        .get_or_create(
            dedupe_key=dedupe_key,
            defaults={
                "rule":
                    rule,

                "agreement":
                    rule.agreement,

                "installment":
                    target.installment,

                "recipient_user":
                    recipient,

                "event":
                    rule.event,

                "channel":
                    rule.channel,

                "title":
                    title,

                "message":
                    message,

                "target_date":
                    target.target_date,

                "trigger_date":
                    trigger_date,
            },
        )
    )


def _notification_content(
    rule,
    target,
):
    agreement = (
        rule.agreement
    )

    portfolio_name = (
        agreement.portfolio.name
    )

    if (
        rule.event
        == (
            PaymentReminderRule
            .Event.AGREEMENT_EXPIRY
        )
    ):
        title = (
            _timed_title(
                before=(
                    "Agreement expires"
                ),
                on=(
                    "Agreement expires "
                    "today"
                ),
                after=(
                    "Agreement expiry "
                    "passed"
                ),
                dated=(
                    "Agreement expiry "
                    "reminder"
                ),
                rule=rule,
            )
        )

        message = (
            f"{agreement.title} for "
            f"{portfolio_name} has an "
            f"end date of "
            f"{target.target_date.isoformat()}."
        )

        return title, message

    installment = (
        target.installment
    )

    amount = (
        f"{target.outstanding_amount:,.2f} "
        f"{agreement.currency}"
    )

    if (
        rule.event
        == (
            PaymentReminderRule
            .Event
            .MILESTONE_EXPECTED
        )
    ):
        title = (
            _timed_title(
                before=(
                    "Milestone payment "
                    "expected"
                ),
                on=(
                    "Milestone payment "
                    "expected today"
                ),
                after=(
                    "Milestone expected "
                    "date passed"
                ),
                dated=(
                    "Milestone payment "
                    "reminder"
                ),
                rule=rule,
            )
        )

        message = (
            f"{installment.title} for "
            f"{portfolio_name} has an "
            f"expected milestone date "
            f"of "
            f"{target.target_date.isoformat()}. "
            f"{amount} remains "
            f"outstanding and the "
            f"confirmed milestone date "
            f"has not been set."
        )

        return title, message

    title = _timed_title(
        before="Payment due",
        on="Payment due today",
        after="Payment overdue",
        dated="Payment reminder",
        rule=rule,
    )

    message = (
        f"{installment.title} for "
        f"{portfolio_name} has "
        f"{amount} outstanding. "
        f"Due date: "
        f"{target.target_date.isoformat()}."
    )

    return title, message


def _timed_title(
    *,
    before,
    on,
    after,
    dated,
    rule,
):
    # A set-date reminder has no offset to describe; its message
    # carries the date that matters.
    if (
        rule.timing
        == (
            PaymentReminderRule
            .Timing.DATE
        )
    ):
        return dated

    if (
        rule.timing
        == (
            PaymentReminderRule
            .Timing.ON
        )
    ):
        return on

    unit = (
        "day"
        if rule.days == 1
        else "days"
    )

    if (
        rule.timing
        == (
            PaymentReminderRule
            .Timing.BEFORE
        )
    ):
        return (
            f"{before} in "
            f"{rule.days} {unit}"
        )

    return (
        f"{after} by "
        f"{rule.days} {unit}"
    )


def _dedupe_key(
    *,
    rule,
    target,
    recipient,
    trigger_date,
):
    raw = (
        f"{rule.pk}|"
        f"{target.kind}|"
        f"{target.target_id}|"
        f"{trigger_date.isoformat()}|"
        f"{recipient.pk}|"
        f"{rule.channel}"
    )

    return hashlib.sha256(
        raw.encode(
            "utf-8"
        )
    ).hexdigest()


def _mark_failed(
    notification,
    message,
):
    notification.status = (
        PaymentNotification
        .Status.FAILED
    )

    notification.sent_at = None

    notification.failure_reason = (
        message
    )

    notification.save(
        update_fields=(
            "attempt_count",
            "last_attempt_at",
            "status",
            "sent_at",
            "failure_reason",
        )
    )

    return notification