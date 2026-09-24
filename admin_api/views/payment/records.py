from admin_api.filters.payment import (
    PaymentFilterError,
    apply_record_filters,
)
from admin_api.forms.payment.record import (
    PaymentAllocationForm,
    PaymentRecordCreateForm,
    PaymentVoidForm,
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
from admin_api.serializers.payment.record import (
    serialize_payment_record,
)
from admin_api.services.payment import (
    PaymentOperationError,
)
from admin_api.services.payment.record import (
    allocate_payment,
    record_payment,
    void_payment,
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
    PaymentRecord,
)


def payment_queryset():
    return (
        PaymentRecord
        .objects
        .select_related(
            "agreement",
            "agreement__portfolio",
            "recorded_by",
        )
        .prefetch_related(
            "allocations__installment"
        )
    )


@nexcode_admin_required
def list_payments_view(
    request,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    try:
        queryset = (
            apply_record_filters(
                payment_queryset(),
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
                    serialize_payment_record(
                        payment
                    )
                    for payment
                    in page.object_list
                ],
                "pagination":
                    pagination,
            },
        }
    )


@nexcode_admin_required
def record_payment_view(
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
        PaymentRecordCreateForm(
            payload
        )
    )

    if not form.is_valid():
        return form_error(
            form
        )

    try:
        payment = record_payment(
            agreement,
            form.cleaned_data,
            recorded_by=(
                request.user
            ),
        )
    except PaymentOperationError as error:
        return operation_error(
            error
        )

    payment = (
        payment_queryset()
        .get(
            pk=payment.pk
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Payment recorded.",
            "data": {
                "payment":
                    serialize_payment_record(
                        payment
                    ),
            },
        },
        status=201,
    )


@nexcode_admin_required
def allocate_payment_view(
    request,
    payment_id,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    payment = (
        PaymentRecord
        .objects
        .filter(
            pk=payment_id
        )
        .first()
    )

    if payment is None:
        return not_found(
            "Payment"
        )

    try:
        payload = parse_json_payload(
            request
        )
    except JsonPayloadError as error:
        return payload_error(
            error
        )

    form = PaymentAllocationForm(
        payload
    )

    if not form.is_valid():
        return form_error(
            form
        )

    try:
        payment = allocate_payment(
            payment,
            form.cleaned_data[
                "allocations"
            ],
        )
    except PaymentOperationError as error:
        return operation_error(
            error
        )

    payment = (
        payment_queryset()
        .get(
            pk=payment.pk
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Payment allocated.",
            "data": {
                "payment":
                    serialize_payment_record(
                        payment
                    ),
            },
        }
    )


@nexcode_admin_required
def void_payment_view(
    request,
    payment_id,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    payment = (
        PaymentRecord
        .objects
        .filter(
            pk=payment_id
        )
        .first()
    )

    if payment is None:
        return not_found(
            "Payment"
        )

    try:
        payload = parse_json_payload(
            request
        )
    except JsonPayloadError as error:
        return payload_error(
            error
        )

    form = PaymentVoidForm(
        payload
    )

    if not form.is_valid():
        return form_error(
            form
        )

    try:
        payment = void_payment(
            payment,
            form.cleaned_data[
                "reason"
            ],
        )
    except PaymentOperationError as error:
        return operation_error(
            error
        )

    payment = (
        payment_queryset()
        .get(
            pk=payment.pk
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Payment voided.",
            "data": {
                "payment":
                    serialize_payment_record(
                        payment
                    ),
            },
        }
    )