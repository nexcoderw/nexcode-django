from django.db import (
    IntegrityError,
)

from admin_api.filters.payment import (
    PaymentFilterError,
    apply_notification_filters,
    apply_reminder_rule_filters,
)
from admin_api.forms.payment.reminder import (
    PaymentReminderRuleCreateForm,
    PaymentReminderRuleUpdateForm,
)
from admin_api.pagination.page_number import (
    PaginationError,
    paginate_queryset,
)
from admin_api.parsers.json_body import (
    JsonPayloadError,
    parse_json_payload,
)
from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.payment.reminder import (
    serialize_payment_notification,
    serialize_reminder_rule,
)
from admin_api.services.payment import (
    PaymentOperationError,
)
from admin_api.services.payment.reminder import (
    create_reminder_rule,
    delete_reminder_rule,
    mark_all_notifications_read,
    mark_notification_read,
    retry_notification,
    update_reminder_rule,
)
from admin_api.views.payment.responses import (
    form_error,
    json_response,
    method_not_allowed,
    not_found,
    operation_error,
    payload_error,
)
from home.models import (
    PaymentAgreement,
    PaymentNotification,
    PaymentReminderRule,
)


def rule_queryset():
    return (
        PaymentReminderRule
        .objects
        .select_related(
            "agreement",
            "agreement__portfolio",
            "created_by",
        )
    )


def notification_queryset():
    return (
        PaymentNotification
        .objects
        .select_related(
            "rule",
            "agreement",
            "agreement__portfolio",
            "installment",
            "recipient_user",
        )
    )


@nexcode_admin_required
def list_reminder_rules_view(
    request,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    try:
        queryset = (
            apply_reminder_rule_filters(
                rule_queryset(),
                request.GET,
            )
        )

        page, pagination = (
            paginate_queryset(
                queryset,
                request.GET,
            )
        )

    except (
        PaymentFilterError,
        PaginationError,
    ) as error:
        return json_response(
            {
                "status": "error",
                "message":
                    str(error),
            },
            status=400,
        )

    return json_response(
        {
            "status": "success",
            "data": {
                "items": [
                    serialize_reminder_rule(
                        rule
                    )
                    for rule
                    in page.object_list
                ],
                "pagination":
                    pagination,
            },
        }
    )


@nexcode_admin_required
def add_reminder_rule_view(
    request,
    agreement_id,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    agreement = (
        PaymentAgreement
        .objects
        .filter(
            pk=agreement_id
        )
        .first()
    )

    if agreement is None:
        return not_found(
            "Payment agreement"
        )

    try:
        payload = parse_json_payload(
            request
        )
    except JsonPayloadError as error:
        return payload_error(
            error
        )

    form = (
        PaymentReminderRuleCreateForm(
            payload
        )
    )

    if not form.is_valid():
        return form_error(
            form
        )

    try:
        rule = create_reminder_rule(
            agreement,
            form.cleaned_data,
            created_by=(
                request.user
            ),
        )

    except PaymentOperationError as error:
        return operation_error(
            error
        )

    except IntegrityError:
        return json_response(
            {
                "status": "error",
                "message": (
                    "This reminder rule "
                    "already exists."
                ),
            },
            status=400,
        )

    rule = (
        rule_queryset()
        .get(
            pk=rule.pk
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Reminder rule created.",
            "data": {
                "rule":
                    serialize_reminder_rule(
                        rule
                    ),
            },
        },
        status=201,
    )


@nexcode_admin_required
def reminder_rule_detail_view(
    request,
    rule_id,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    rule = (
        rule_queryset()
        .filter(
            pk=rule_id
        )
        .first()
    )

    if rule is None:
        return not_found(
            "Reminder rule"
        )

    return json_response(
        {
            "status": "success",
            "data": {
                "rule":
                    serialize_reminder_rule(
                        rule
                    ),
            },
        }
    )


@nexcode_admin_required
def update_reminder_rule_view(
    request,
    rule_id,
):
    if request.method != "PATCH":
        return method_not_allowed(
            ["PATCH"]
        )

    rule = (
        rule_queryset()
        .filter(
            pk=rule_id
        )
        .first()
    )

    if rule is None:
        return not_found(
            "Reminder rule"
        )

    try:
        payload = parse_json_payload(
            request
        )
    except JsonPayloadError as error:
        return payload_error(
            error
        )

    form = (
        PaymentReminderRuleUpdateForm(
            payload,
            rule=rule,
        )
    )

    if not form.is_valid():
        return form_error(
            form
        )

    try:
        rule = update_reminder_rule(
            rule,
            form,
        )

    except PaymentOperationError as error:
        return operation_error(
            error
        )

    except IntegrityError:
        return json_response(
            {
                "status": "error",
                "message": (
                    "This reminder rule "
                    "already exists."
                ),
            },
            status=400,
        )

    rule = (
        rule_queryset()
        .get(
            pk=rule.pk
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Reminder rule updated.",
            "data": {
                "rule":
                    serialize_reminder_rule(
                        rule
                    ),
            },
        }
    )


@nexcode_admin_required
def delete_reminder_rule_view(
    request,
    rule_id,
):
    if request.method != "DELETE":
        return method_not_allowed(
            ["DELETE"]
        )

    rule = (
        PaymentReminderRule
        .objects
        .filter(
            pk=rule_id
        )
        .first()
    )

    if rule is None:
        return not_found(
            "Reminder rule"
        )

    delete_reminder_rule(
        rule
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Reminder rule deleted.",
        }
    )


@nexcode_admin_required
def list_payment_notifications_view(
    request,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    try:
        queryset = (
            apply_notification_filters(
                notification_queryset()
                .filter(
                    recipient_user=(
                        request.user
                    )
                ),
                request.GET,
            )
        )

        page, pagination = (
            paginate_queryset(
                queryset,
                request.GET,
            )
        )

    except (
        PaymentFilterError,
        PaginationError,
    ) as error:
        return json_response(
            {
                "status": "error",
                "message":
                    str(error),
            },
            status=400,
        )

    return json_response(
        {
            "status": "success",
            "data": {
                "items": [
                    serialize_payment_notification(
                        notification
                    )
                    for notification
                    in page.object_list
                ],
                "pagination":
                    pagination,
            },
        }
    )


@nexcode_admin_required
def mark_notification_read_view(
    request,
    notification_id,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    notification = (
        notification_queryset()
        .filter(
            pk=notification_id,
            recipient_user=(
                request.user
            ),
        )
        .first()
    )

    if notification is None:
        return not_found(
            "Payment notification"
        )

    notification = (
        mark_notification_read(
            notification
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Notification marked "
                "as read.",
            "data": {
                "notification":
                    serialize_payment_notification(
                        notification
                    ),
            },
        }
    )


@nexcode_admin_required
def mark_all_notifications_read_view(
    request,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    count = (
        mark_all_notifications_read(
            request.user
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Notifications marked "
                "as read.",
            "data": {
                "updated_count":
                    count,
            },
        }
    )


@nexcode_admin_required
def retry_notification_view(
    request,
    notification_id,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    notification = (
        notification_queryset()
        .filter(
            pk=notification_id,
            recipient_user=(
                request.user
            ),
        )
        .first()
    )

    if notification is None:
        return not_found(
            "Payment notification"
        )

    try:
        notification = (
            retry_notification(
                notification
            )
        )

    except PaymentOperationError as error:
        return operation_error(
            error
        )

    notification = (
        notification_queryset()
        .get(
            pk=notification.pk
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Notification delivery "
                "retried.",
            "data": {
                "notification":
                    serialize_payment_notification(
                        notification
                    ),
            },
        }
    )