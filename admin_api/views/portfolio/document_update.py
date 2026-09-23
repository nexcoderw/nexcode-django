from admin_api.forms.portfolio import (
    PortfolioDocumentUpdateForm,
)
from admin_api.parsers.json_body import (
    JsonPayloadError,
    parse_json_payload,
)
from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.portfolio import (
    serialize_portfolio_document,
)
from admin_api.services.portfolio import (
    update_portfolio_document,
)
from admin_api.views.portfolio.responses import (
    document_not_found,
    form_error,
    json_response,
    method_not_allowed,
    payload_error,
)
from home.models import PortfolioDocument


@nexcode_admin_required
def update_portfolio_document_view(
    request,
    document_id,
):
    if request.method != "PATCH":
        return method_not_allowed(
            ["PATCH"]
        )

    document = (
        PortfolioDocument.objects
        .select_related(
            "portfolio"
        )
        .filter(
            pk=document_id
        )
        .first()
    )

    if document is None:
        return document_not_found()

    try:
        payload = parse_json_payload(
            request
        )
    except JsonPayloadError as error:
        return payload_error(
            error
        )

    form = (
        PortfolioDocumentUpdateForm(
            payload,
            document=document,
        )
    )

    if not form.is_valid():
        return form_error(form)

    document = (
        update_portfolio_document(
            document,
            form,
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Document link updated.",
            "data": {
                "document":
                    serialize_portfolio_document(
                        document
                    ),
            },
        }
    )