from admin_api.filters.payment import (
    PaymentFilterError,
    apply_agreement_filters,
)
from admin_api.forms.payment.agreement import (
    PaymentAgreementCreateForm,
    PaymentAgreementUpdateForm,
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
from admin_api.serializers.payment.agreement import (
    serialize_agreement,
)
from admin_api.services.payment import (
    PaymentOperationError,
)
from admin_api.services.payment.agreement import (
    create_agreement,
    delete_agreement,
    update_agreement,
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
)


@nexcode_admin_required
def list_agreements_view(
    request,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    try:
        queryset = (
            apply_agreement_filters(
                PaymentAgreement
                .objects
                .select_related(
                    "portfolio"
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
                "message": str(
                    error
                ),
            },
            status=400,
        )

    return json_response(
        {
            "status": "success",
            "data": {
                "items": [
                    serialize_agreement(
                        item
                    )
                    for item
                    in page.object_list
                ],
                "pagination":
                    pagination,
            },
        }
    )


@nexcode_admin_required
def add_agreement_view(
    request,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
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
        PaymentAgreementCreateForm(
            payload
        )
    )

    if not form.is_valid():
        return form_error(
            form
        )

    agreement = create_agreement(
        form.cleaned_data
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Payment agreement "
                "created.",
            "data": {
                "agreement":
                    serialize_agreement(
                        agreement
                    ),
            },
        },
        status=201,
    )


@nexcode_admin_required
def agreement_detail_view(
    request,
    agreement_id,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    agreement = (
        PaymentAgreement
        .objects
        .select_related(
            "portfolio"
        )
        .filter(
            pk=agreement_id
        )
        .first()
    )

    if agreement is None:
        return not_found(
            "Payment agreement"
        )

    return json_response(
        {
            "status": "success",
            "data": {
                "agreement":
                    serialize_agreement(
                        agreement
                    ),
            },
        }
    )


@nexcode_admin_required
def update_agreement_view(
    request,
    agreement_id,
):
    if request.method != "PATCH":
        return method_not_allowed(
            ["PATCH"]
        )

    agreement = (
        PaymentAgreement
        .objects
        .select_related(
            "portfolio"
        )
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
        PaymentAgreementUpdateForm(
            payload,
            agreement=agreement,
        )
    )

    if not form.is_valid():
        return form_error(
            form
        )

    try:
        agreement = update_agreement(
            agreement,
            form,
        )
    except PaymentOperationError as error:
        return operation_error(
            error
        )

    return json_response(
        {
            "status": "success",
            "message":
                "Payment agreement "
                "updated.",
            "data": {
                "agreement":
                    serialize_agreement(
                        agreement
                    ),
            },
        }
    )


@nexcode_admin_required
def delete_agreement_view(
    request,
    agreement_id,
):
    if request.method != "DELETE":
        return method_not_allowed(
            ["DELETE"]
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
        delete_agreement(
            agreement
        )
    except PaymentOperationError as error:
        return operation_error(
            error
        )

    return json_response(
        {
            "status": "success",
            "message":
                "Draft payment "
                "agreement deleted.",
        }
    )