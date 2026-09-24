from django.db.models import Q


ALLOWED_TEAM_ORDERINGS = {
    "display_order",
    "-display_order",
    "name",
    "-name",
    "position",
    "-position",
    "created_at",
    "-created_at",
    "updated_at",
    "-updated_at",
}


class TeamFilterError(
    ValueError
):
    pass


def apply_team_filters(
    queryset,
    query_params,
):
    search = (
        query_params.get(
            "search",
            "",
        ).strip()
    )

    # The admin lists members in the order the public site shows them.
    ordering = (
        query_params.get(
            "ordering",
            "display_order",
        ).strip()
    )

    if (
        ordering
        not in ALLOWED_TEAM_ORDERINGS
    ):
        raise TeamFilterError(
            "Invalid ordering."
        )

    if search:
        queryset = queryset.filter(
            Q(
                name__icontains=search
            )
            | Q(
                position__icontains=search
            )
            | Q(
                linkedin__icontains=search
            )
            | Q(
                github__icontains=search
            )
        )

    # Members sharing a position fall back to name, as on the public site.
    return queryset.order_by(
        ordering,
        "name",
        "pk",
    )