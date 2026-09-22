from django.db.models import Q


ALLOWED_TEAM_ORDERINGS = {
    "name",
    "-name",
    "position",
    "-position",
    "created_at",
    "-created_at",
    "updated_at",
    "-updated_at",
}


def apply_team_filters(
    queryset,
    query_params,
):
    search = (
        query_params.get(
            "search",
            ""
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
        not in ALLOWED_TEAM_ORDERINGS
    ):
        raise ValueError(
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

    return queryset.order_by(
        ordering,
        "pk",
    )