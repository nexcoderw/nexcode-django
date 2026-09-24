from django.db.models import Q


ALLOWED_CLIENT_ORDERINGS = {
    "name",
    "-name",
    "created_at",
    "-created_at",
    "updated_at",
    "-updated_at",
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

    if search:
        queryset = (
            queryset.filter(
                Q(
                    name__icontains=search
                )
                | Q(
                    email__icontains=search
                )
                | Q(
                    phone_number__icontains=(
                        search
                    )
                )
            )
        )

    return queryset.order_by(
        ordering,
        "pk",
    )
