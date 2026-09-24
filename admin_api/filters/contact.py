from django.db.models import Q


ALLOWED_CONTACT_ORDERINGS = {
    "created_at",
    "-created_at",
    "name",
    "-name",
}

CONTACT_STATUSES = {
    "new",
    "replied",
}


class ContactFilterError(
    ValueError
):
    pass


def apply_contact_filters(
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
        ALLOWED_CONTACT_ORDERINGS
    ):
        raise ContactFilterError(
            "Invalid ordering."
        )

    if (
        status
        and status
        not in CONTACT_STATUSES
    ):
        raise ContactFilterError(
            "Invalid status."
        )

    if status:
        queryset = queryset.filter(
            replied_at__isnull=(
                status == "new"
            )
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
                    subject__icontains=search
                )
                | Q(
                    ip_address__startswith=(
                        search
                    )
                )
            )
        )

    return queryset.order_by(
        ordering,
        "pk",
    )
