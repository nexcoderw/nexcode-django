from django.contrib.auth import (
    get_user_model,
)
from django.db import transaction
from django.utils import timezone

from admin_api.constants import (
    NEXCODE_ADMIN_GROUP_NAME,
)
from admin_api.forms.payment.reminder import (
    REMINDER_RULE_FIELDS,
)
from admin_api.services.payment import (
    PaymentOperationError,
)
from home.models import (
    PaymentAgreement,
    PaymentNotification,
    PaymentReminderRule,
)
from home.services.payment.reminder import (
    deliver_payment_notification,
    process_payment_reminders,
)


def admin_reminder_recipients():
    User = get_user_model()

    return (
        User.objects
        .filter(
            is_active=True,
            groups__name=(
                NEXCODE_ADMIN_GROUP_NAME
            ),
        )
        .distinct()
    )


def process_admin_payment_reminders(
    *,
    on_date=None,
):
    return process_payment_reminders(
        recipients=(
            admin_reminder_recipients()
        ),
        on_date=on_date,
    )


@transaction.atomic
def create_reminder_rule(
    agreement,
    cleaned_data,
    *,
    created_by,
):
    agreement = (
        PaymentAgreement
        .objects
        .select_for_update()
        .get(
            pk=agreement.pk
        )
    )

    _assert_rule_allowed(
        agreement
    )

    rule = PaymentReminderRule(
        agreement=agreement,
        event=cleaned_data[
            "event"
        ],
        timing=cleaned_data[
            "timing"
        ],
        days=(
            cleaned_data.get(
                "days"
            )
            or 0
        ),
        remind_on=cleaned_data.get(
            "remind_on"
        ),
        channel=(
            cleaned_data.get(
                "channel"
            )
            or (
                PaymentReminderRule
                .Channel.IN_APP
            )
        ),
        is_enabled=(
            cleaned_data.get(
                "is_enabled",
                True,
            )
        ),
        created_by=created_by,
    )

    _normalize_timing(
        rule
    )

    rule.full_clean()
    rule.save()

    return rule


@transaction.atomic
def update_reminder_rule(
    rule,
    form,
):
    rule = (
        PaymentReminderRule
        .objects
        .select_for_update()
        .select_related(
            "agreement"
        )
        .get(
            pk=rule.pk
        )
    )

    _assert_rule_allowed(
        rule.agreement
    )

    data = form.cleaned_data

    for field in (
        REMINDER_RULE_FIELDS
    ):
        if field not in form.data:
            continue

        setattr(
            rule,
            field,
            data.get(field),
        )

    _normalize_timing(
        rule
    )

    rule.full_clean()
    rule.save()

    return rule


@transaction.atomic
def delete_reminder_rule(
    rule,
):
    rule = (
        PaymentReminderRule
        .objects
        .select_for_update()
        .get(
            pk=rule.pk
        )
    )

    rule.delete()


def mark_notification_read(
    notification,
):
    if notification.read_at:
        return notification

    notification.read_at = (
        timezone.now()
    )

    notification.save(
        update_fields=(
            "read_at",
        )
    )

    return notification


def mark_all_notifications_read(
    user,
):
    return (
        PaymentNotification
        .objects
        .filter(
            recipient_user=user,
            read_at__isnull=True,
        )
        .update(
            read_at=timezone.now()
        )
    )


def retry_notification(
    notification,
):
    if (
        notification.status
        != (
            PaymentNotification
            .Status.FAILED
        )
    ):
        raise PaymentOperationError(
            (
                "Only failed "
                "notifications can "
                "be retried."
            )
        )

    return (
        deliver_payment_notification(
            notification
        )
    )


def _assert_rule_allowed(
    agreement,
):
    if agreement.status in (
        PaymentAgreement
        .Status.COMPLETED,
        PaymentAgreement
        .Status.CANCELLED,
    ):
        raise PaymentOperationError(
            (
                "Reminder rules cannot "
                "be modified on a "
                "completed or "
                "cancelled agreement."
            )
        )


def _normalize_timing(
    rule,
):
    """
    Keep only what the rule's timing uses: a set date needs no offset,
    and an offset needs no date. Switching a rule's timing therefore
    never leaves a stale value behind.
    """

    if (
        rule.timing
        == (
            PaymentReminderRule
            .Timing.DATE
        )
    ):
        rule.days = 0
    else:
        rule.remind_on = None
