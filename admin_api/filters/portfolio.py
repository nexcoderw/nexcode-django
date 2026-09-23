from django.db.models import Q

from home.models import Portfolio


ALLOWED_PORTFOLIO_ORDERINGS = {
    "name",
    "-name",
    "created_at",
    "-created_at",
    "updated_at",
    "-updated_at",
    "published_at",
    "-published_at",
    "deadline_date",
    "-deadline_date",
}

VALID_CATEGORIES = {
    value
    for value, _
    in Portfolio.Category.choices
}

VALID_PROJECT_TYPES = {
    value
    for value, _
    in Portfolio.ProjectType.choices
}

VALID_STATUSES = {
    value
    for value, _
    in Portfolio.Status.choices
}


class PortfolioFilterError(
    ValueError
):
    pass


def apply_portfolio_filters(
    queryset,
    query_params,
):
    search = (
        query_params.get(
            "search",
            "",
        ).strip()
    )

    category = (
        query_params.get(
            "category",
            "",
        ).strip()
    )

    project_type = (
        query_params.get(
            "project_type",
            "",
        ).strip()
    )

    status = (
        query_params.get(
            "status",
            "",
        ).strip()
    )

    team_member_id = (
        query_params.get(
            "team_member_id",
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
        ALLOWED_PORTFOLIO_ORDERINGS
    ):
        raise PortfolioFilterError(
            "Invalid ordering."
        )

    if (
        category
        and category
        not in VALID_CATEGORIES
    ):
        raise PortfolioFilterError(
            "Invalid category."
        )

    if (
        project_type
        and project_type
        not in VALID_PROJECT_TYPES
    ):
        raise PortfolioFilterError(
            "Invalid project type."
        )

    if (
        status
        and status
        not in VALID_STATUSES
    ):
        raise PortfolioFilterError(
            "Invalid status."
        )

    if search:
        queryset = queryset.filter(
            Q(
                name__icontains=search
            )
            | Q(
                summary__icontains=search
            )
            | Q(
                description__icontains=search
            )
        )

    if category:
        queryset = queryset.filter(
            category=category
        )

    if project_type:
        queryset = queryset.filter(
            project_type=project_type
        )

    if status:
        queryset = queryset.filter(
            status=status
        )

    if team_member_id:
        try:
            team_member_id = int(
                team_member_id
            )
        except ValueError:
            raise PortfolioFilterError(
                (
                    "team_member_id "
                    "must be an integer."
                )
            )

        if team_member_id < 1:
            raise PortfolioFilterError(
                (
                    "team_member_id "
                    "must be positive."
                )
            )

        queryset = queryset.filter(
            team_members__pk=(
                team_member_id
            )
        )

    return (
        queryset
        .distinct()
        .order_by(
            ordering,
            "pk",
        )
    )