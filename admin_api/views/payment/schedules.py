from admin_api.forms.payment.schedule import (
    ContractScheduleForm,
    MaintenanceScheduleForm,
)
from admin_api.parsers.json_body import (
    JsonPayloadError,
    parse_json_payload,
)
from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.payment.installment import (
    serialize_installment,
)
from admin_api.services.payment import (
    PaymentOperationError,
)
from admin_api.services.payment.schedule import (
    create_contract_schedule,
    create_maintenance_schedule,
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

from django.core.exceptions import (
    ValidationError,
)

@nexcode_admin_required
def generate_contract_schedule_view(
    request,
    agreement_id,
):
    return _generate_schedule(
        request,
        agreement_id,
        ContractScheduleForm,
        create_contract_schedule,
    )


@nexcode_admin_required
def generate_maintenance_schedule_view(
    request,
    agreement_id,
):
    return _generate_schedule(
        request,
        agreement_id,
        MaintenanceScheduleForm,
        create_maintenance_schedule,
    )


def _generate_schedule(
    request,
    agreement_id,
    form_class,
    service,
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

    form = form_class(
        payload
    )

    if not form.is_valid():
        return form_error(
            form
        )

    try:
        installments = service(
            agreement,
            form.cleaned_data,
        )
    except PaymentOperationError as error:
        return operation_error(
            error
        )
    except ValidationError as error:
        return json_response(
            {
                "status": "error",
                "message":
                    "; ".join(
                        error.messages
                    ),
            },
            status=400,
        )
    except (
        PaymentOperationError,
        Exception,
    ) as error:
        # ValidationError from the Step 39
        # scheduler and operation errors both
        # represent invalid administrator input.
        if isinstance(
            error,
            PaymentOperationError,
        ):
            return operation_error(
                error
            )

        if isinstance(
            error,
            ValidationError,
        ):
            return json_response(
                {
                    "status": "error",
                    "message":
                        "; ".join(
                            error.messages
                        ),
                },
                status=400,
            )

        raise

    return json_response(
        {
            "status": "success",
            "message":
                "Payment schedule "
                "created.",
            "data": {
                "items": [
                    serialize_installment(
                        item
                    )
                    for item
                    in installments
                ],
            },
        },
        status=201,
    )