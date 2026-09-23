from django.db.models import Q

from home.models import Client


ALLOWED_CLIENT_ORDERINGS = {
    "name",
    "-name",
    "company_name",
    "-company_name",
    "status",
    "-status",
    "created_at",
    "-created_at",
    "updated_at",
    "-updated_at",
}

VALID_CLIENT_STATUSES = {
    value
    for value, _
    in Client.Status.choices
}


class ClientFilterError(
    ValueError
):
    pass


def apply_client_filters(
    queryset,
    query_params,
):
    search = (
        query_params.get(
            "search",
            "",
        ).strip()
    )

    status = (
        query_params.get(
            "status",
            "",
        ).strip()
    )

    ordering = (
        query_params.get(
            "ordering",
            "-created_at",
        ).strip()
    )

    if (
        ordering
        not in
        ALLOWED_CLIENT_ORDERINGS
    ):
        raise ClientFilterError(
            "Invalid ordering."
        )

    if (
        status
        and status
        not in VALID_CLIENT_STATUSES
    ):
        raise ClientFilterError(
            "Invalid status."
        )

    if search:
        queryset = (
            queryset.filter(
                Q(
                    name__icontains=search
                )
                | Q(
                    company_name__icontains=(
                        search
                    )
                )
                | Q(
                    email__icontains=search
                )
                | Q(
                    phone__icontains=search
                )
                | Q(
                    location__icontains=search
                )
            )
        )

    if status:
        queryset = queryset.filter(
            status=status
        )

    return queryset.order_by(
        ordering,
        "pk",
    )