from datetime import date

from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from admin_api.services.payment.reminder import (
    admin_reminder_recipients,
    process_admin_payment_reminders,
)
from home.models import (
    PaymentNotification,
)
from home.services.payment.reminder import (
    retry_failed_notifications,
)


class Command(
    BaseCommand
):
    help = (
        "Generate payment reminders "
        "due on a calendar date."
    )

    def add_arguments(
        self,
        parser,
    ):
        parser.add_argument(
            "--date",
            dest="process_date",
            help=(
                "Process YYYY-MM-DD "
                "instead of today."
            ),
        )

        parser.add_argument(
            "--retry-failed",
            action="store_true",
            help=(
                "Retry failed email "
                "notifications."
            ),
        )

    def handle(
        self,
        *args,
        **options,
    ):
        process_date = (
            _parse_date(
                options.get(
                    "process_date"
                )
            )
        )

        result = (
            process_admin_payment_reminders(
                on_date=(
                    process_date
                )
            )
        )

        self.stdout.write(
            (
                "Payment reminders: "
                f"{result.created} created, "
                f"{result.sent} sent, "
                f"{result.failed} failed, "
                f"{result.skipped} skipped."
            )
        )

        if not options[
            "retry_failed"
        ]:
            return

        admin_ids = (
            admin_reminder_recipients()
            .values_list(
                "pk",
                flat=True,
            )
        )

        failed = (
            PaymentNotification
            .objects
            .filter(
                recipient_user_id__in=(
                    admin_ids
                ),
                status=(
                    PaymentNotification
                    .Status.FAILED
                ),
            )
            .select_related(
                "recipient_user"
            )
        )

        retry_result = (
            retry_failed_notifications(
                notifications=failed,
            )
        )

        self.stdout.write(
            (
                "Retries: "
                f"{retry_result.sent} sent, "
                f"{retry_result.failed} failed, "
                f"{retry_result.skipped} skipped."
            )
        )


def _parse_date(
    value,
):
    if not value:
        return None

    try:
        return date.fromisoformat(
            value
        )
    except ValueError as error:
        raise CommandError(
            "--date must use "
            "YYYY-MM-DD."
        ) from error