from decimal import Decimal

from django.core.exceptions import (
    ValidationError,
)
from django.db.models import (
    DecimalField,
    Q,
    Sum,
    Value,
)
from django.db.models.functions import (
    Coalesce,
)

from admin_api.forms.payment.installment import (
    InstallmentWaiverForm,
    MilestoneConfirmationForm,
    PaymentInstallmentCreateForm,
    PaymentInstallmentUpdateForm,
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
from admin_api.services.payment.installment import (
    confirm_milestone,
    create_installment,
    delete_installment,
    update_installment,
    waive_installment,
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
    PaymentInstallment,
    PaymentRecord,
)


MONEY_FIELD = DecimalField(
    max_digits=18,
    decimal_places=2,
)


def installment_queryset():
    """
    Return installments with the amount received from valid posted
    payments already calculated.

    This prevents the installment serializer from issuing a separate
    allocation query for every row in list responses.
    """

    return (
        PaymentInstallment
        .objects
        .select_related(
            "agreement",
            "agreement__portfolio",
        )
        .annotate(
            posted_paid_amount=Coalesce(
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
                    Decimal(
                        "0.00"
                    )
                ),
                output_field=MONEY_FIELD,
            )
        )
    )


@nexcode_admin_required
def list_installments_view(
    request,
    agreement_id,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    agreement_exists = (
        PaymentAgreement
        .objects
        .filter(
            pk=agreement_id
        )
        .exists()
    )

    if not agreement_exists:
        return not_found(
            "Payment agreement"
        )

    installments = (
        installment_queryset()
        .filter(
            agreement_id=(
                agreement_id
            )
        )
        .order_by(
            "sequence",
            "pk",
        )
    )

    return json_response(
        {
            "status": "success",
            "data": {
                "items": [
                    serialize_installment(
                        installment
                    )
                    for installment
                    in installments
                ],
            },
        }
    )


@nexcode_admin_required
def add_installment_view(
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
        PaymentInstallmentCreateForm(
            payload
        )
    )

    if not form.is_valid():
        return form_error(
            form
        )

    try:
        installment = (
            create_installment(
                agreement,
                form.cleaned_data,
            )
        )
    except PaymentOperationError as error:
        return operation_error(
            error
        )
    except ValidationError as error:
        return validation_error(
            error
        )

    installment = (
        installment_queryset()
        .get(
            pk=installment.pk
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Installment created.",
            "data": {
                "installment":
                    serialize_installment(
                        installment
                    ),
            },
        },
        status=201,
    )


@nexcode_admin_required
def update_installment_view(
    request,
    installment_id,
):
    if request.method != "PATCH":
        return method_not_allowed(
            ["PATCH"]
        )

    installment = (
        PaymentInstallment
        .objects
        .select_related(
            "agreement"
        )
        .filter(
            pk=installment_id
        )
        .first()
    )

    if installment is None:
        return not_found(
            "Installment"
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
        PaymentInstallmentUpdateForm(
            payload,
            installment=installment,
        )
    )

    if not form.is_valid():
        return form_error(
            form
        )

    try:
        installment = (
            update_installment(
                installment,
                form,
            )
        )
    except PaymentOperationError as error:
        return operation_error(
            error
        )
    except ValidationError as error:
        return validation_error(
            error
        )

    installment = (
        installment_queryset()
        .get(
            pk=installment.pk
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Installment updated.",
            "data": {
                "installment":
                    serialize_installment(
                        installment
                    ),
            },
        }
    )


@nexcode_admin_required
def delete_installment_view(
    request,
    installment_id,
):
    if request.method != "DELETE":
        return method_not_allowed(
            ["DELETE"]
        )

    installment = (
        PaymentInstallment
        .objects
        .filter(
            pk=installment_id
        )
        .first()
    )

    if installment is None:
        return not_found(
            "Installment"
        )

    try:
        delete_installment(
            installment
        )
    except PaymentOperationError as error:
        return operation_error(
            error
        )

    return json_response(
        {
            "status": "success",
            "message":
                "Installment deleted.",
        }
    )


@nexcode_admin_required
def confirm_milestone_view(
    request,
    installment_id,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    installment = (
        PaymentInstallment
        .objects
        .select_related(
            "agreement"
        )
        .filter(
            pk=installment_id
        )
        .first()
    )

    if installment is None:
        return not_found(
            "Installment"
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
        MilestoneConfirmationForm(
            payload
        )
    )

    if not form.is_valid():
        return form_error(
            form
        )

    try:
        installment = (
            confirm_milestone(
                installment,
                form.cleaned_data[
                    "due_date"
                ],
            )
        )
    except PaymentOperationError as error:
        return operation_error(
            error
        )
    except ValidationError as error:
        return validation_error(
            error
        )

    installment = (
        installment_queryset()
        .get(
            pk=installment.pk
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Milestone date confirmed.",
            "data": {
                "installment":
                    serialize_installment(
                        installment
                    ),
            },
        }
    )


@nexcode_admin_required
def waive_installment_view(
    request,
    installment_id,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    installment = (
        PaymentInstallment
        .objects
        .select_related(
            "agreement"
        )
        .filter(
            pk=installment_id
        )
        .first()
    )

    if installment is None:
        return not_found(
            "Installment"
        )

    try:
        payload = parse_json_payload(
            request
        )
    except JsonPayloadError as error:
        return payload_error(
            error
        )

    form = InstallmentWaiverForm(
        payload
    )

    if not form.is_valid():
        return form_error(
            form
        )

    try:
        installment = (
            waive_installment(
                installment,
                form.cleaned_data[
                    "reason"
                ],
            )
        )
    except PaymentOperationError as error:
        return operation_error(
            error
        )
    except ValidationError as error:
        return validation_error(
            error
        )

    installment = (
        installment_queryset()
        .get(
            pk=installment.pk
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Installment waived.",
            "data": {
                "installment":
                    serialize_installment(
                        installment
                    ),
            },
        }
    )


def validation_error(
    error,
):
    """
    Convert model-level Django validation errors into the same stable
    JSON shape used by the rest of the admin API.
    """

    if hasattr(
        error,
        "message_dict",
    ):
        errors = {
            field: [
                str(message)
                for message
                in messages
            ]
            for field, messages
            in error.message_dict.items()
        }
    else:
        errors = {
            "__all__": [
                str(message)
                for message
                in error.messages
            ],
        }

    return json_response(
        {
            "status": "error",
            "message":
                "Check the submitted "
                "fields.",
            "errors": errors,
        },
        status=400,
    )