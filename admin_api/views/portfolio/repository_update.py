from admin_api.forms.portfolio import (
    PortfolioRepositoryUpdateForm,
)
from admin_api.parsers.json_body import (
    JsonPayloadError,
    parse_json_payload,
)
from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.portfolio import (
    serialize_portfolio_repository,
)
from admin_api.services.portfolio import (
    update_portfolio_repository,
)
from admin_api.views.portfolio.responses import (
    form_error,
    json_response,
    method_not_allowed,
    payload_error,
    repository_not_found,
)
from home.models import PortfolioRepository


@nexcode_admin_required
def update_portfolio_repository_view(
    request,
    repository_id,
):
    if request.method != "PATCH":
        return method_not_allowed(
            ["PATCH"]
        )

    repository = (
        PortfolioRepository.objects
        .select_related(
            "portfolio"
        )
        .filter(
            pk=repository_id
        )
        .first()
    )

    if repository is None:
        return repository_not_found()

    try:
        payload = parse_json_payload(
            request
        )
    except JsonPayloadError as error:
        return payload_error(
            error
        )

    form = (
        PortfolioRepositoryUpdateForm(
            payload,
            repository=repository,
        )
    )

    if not form.is_valid():
        return form_error(form)

    repository = (
        update_portfolio_repository(
            repository,
            form,
        )
    )

    return json_response(
        {
            "status": "success",
            "message":
                "Repository updated.",
            "data": {
                "repository":
                    serialize_portfolio_repository(
                        repository
                    ),
            },
        }
    )