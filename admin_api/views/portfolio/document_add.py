from admin_api.forms.portfolio import (
    PortfolioDocumentCreateForm,
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
    create_portfolio_document,
)
from admin_api.views.portfolio.responses import (
    form_error,
    json_response,
    method_not_allowed,
    payload_error,
    portfolio_not_found,
)
from home.models import Portfolio


@nexcode_admin_required
def add_portfolio_document_view(
    request,
    portfolio_id,
):
    if request.method != "POST":
        return method_not_allowed(
            ["POST"]
        )

    portfolio = (
        Portfolio.objects.filter(
            pk=portfolio_id
        ).first()
    )

    if portfolio is None:
        return portfolio_not_found()

    try:
        payload = parse_json_payload(
            request
        )
    except JsonPayloadError as error:
        return payload_error(
            error
        )

    form = (
        PortfolioDocumentCreateForm(
            payload,
            portfolio=portfolio,
        )
    )

    if not form.is_valid():
        return form_error(form)

    document = (
        create_portfolio_document(
            portfolio,
            form,
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Document link added.",
            "data": {
                "document":
                    serialize_portfolio_document(
                        document
                    ),
            },
        },
        status=201,
    )