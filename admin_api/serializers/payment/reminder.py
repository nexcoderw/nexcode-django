def serialize_reminder_rule(
    rule,
):
    return {
        "id":
            rule.pk,

        "agreement": {
            "id":
                rule.agreement_id,

            "title":
                rule
                .agreement
                .title,

            "portfolio": {
                "id":
                    rule
                    .agreement
                    .portfolio_id,

                "name":
                    rule
                    .agreement
                    .portfolio
                    .name,
            },
        },

        "event":
            rule.event,

        "timing":
            rule.timing,

        "days":
            rule.days,

        "channel":
            rule.channel,

        "is_enabled":
            rule.is_enabled,

        "created_by_id":
            rule.created_by_id,

        "created_at":
            rule
            .created_at
            .isoformat(),

        "updated_at":
            rule
            .updated_at
            .isoformat(),
    }


def serialize_payment_notification(
    notification,
):
    return {
        "id":
            notification.pk,

        "rule_id":
            notification.rule_id,

        "agreement": {
            "id":
                notification
                .agreement_id,

            "title":
                notification
                .agreement
                .title,

            "portfolio": {
                "id":
                    notification
                    .agreement
                    .portfolio_id,

                "name":
                    notification
                    .agreement
                    .portfolio
                    .name,
            },
        },

        "installment": (
            {
                "id":
                    notification
                    .installment_id,

                "title":
                    notification
                    .installment
                    .title,
            }
            if notification
            .installment_id
            else None
        ),

        "event":
            notification.event,

        "channel":
            notification.channel,

        "title":
            notification.title,

        "message":
            notification.message,

        "target_date":
            notification
            .target_date
            .isoformat(),

        "trigger_date":
            notification
            .trigger_date
            .isoformat(),

        "status":
            notification.status,

        "attempt_count":
            notification
            .attempt_count,

        "last_attempt_at":
            (
                notification
                .last_attempt_at
                .isoformat()
                if notification
                .last_attempt_at
                else None
            ),

        "sent_at":
            (
                notification
                .sent_at
                .isoformat()
                if notification
                .sent_at
                else None
            ),

        "read_at":
            (
                notification
                .read_at
                .isoformat()
                if notification
                .read_at
                else None
            ),

        "is_read":
            notification
            .read_at is not None,

        "failure_reason":
            (
                notification
                .failure_reason
                or None
            ),

        "created_at":
            notification
            .created_at
            .isoformat(),
    }