from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.team import (
    serialize_team_member,
)
from home.models import Team


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

ALLOWED_ORDERINGS = {
    "name",
    "-name",
    "position",
    "-position",
    "created_at",
    "-created_at",
    "updated_at",
    "-updated_at",
}


@nexcode_admin_required
def team_list_view(request):
    if request.method != "GET":
        return _method_not_allowed(
            ["GET"]
        )

    query, error_response = (
        _parse_list_query(request)
    )

    if error_response is not None:
        return error_response

    queryset = Team.objects.all()

    search = query["search"]

    if search:
        queryset = queryset.filter(
            Q(name__icontains=search)
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

    queryset = queryset.order_by(
        query["ordering"],
        "pk",
    )

    paginator = Paginator(
        queryset,
        query["page_size"],
    )

    page = paginator.get_page(
        query["page"]
    )

    response = JsonResponse(
        {
            "status": "success",
            "data": {
                "items": [
                    serialize_team_member(
                        team_member
                    )
                    for team_member
                    in page.object_list
                ],
                "pagination": {
                    "page": page.number,
                    "page_size": (
                        query["page_size"]
                    ),
                    "total_items": (
                        paginator.count
                    ),
                    "total_pages": (
                        paginator.num_pages
                    ),
                    "has_next": (
                        page.has_next()
                    ),
                    "has_previous": (
                        page.has_previous()
                    ),
                },
            },
        }
    )

    response["Cache-Control"] = (
        "no-store"
    )

    return response


@nexcode_admin_required
def team_detail_view(
    request,
    team_id,
):
    if request.method != "GET":
        return _method_not_allowed(
            ["GET"]
        )

    try:
        team_member = Team.objects.get(
            pk=team_id
        )
    except Team.DoesNotExist:
        return JsonResponse(
            {
                "status": "error",
                "message":
                    "Team member not found.",
            },
            status=404,
        )

    response = JsonResponse(
        {
            "status": "success",
            "data": {
                "team_member":
                    serialize_team_member(
                        team_member
                    ),
            },
        }
    )

    response["Cache-Control"] = (
        "no-store"
    )

    return response


def _parse_list_query(request):
    search = (
        request.GET.get(
            "search",
            "",
        ).strip()
    )

    ordering = (
        request.GET.get(
            "ordering",
            "-created_at",
        ).strip()
    )

    if (
        ordering
        not in ALLOWED_ORDERINGS
    ):
        return (
            None,
            JsonResponse(
                {
                    "status": "error",
                    "message":
                        "Invalid ordering.",
                },
                status=400,
            ),
        )

    page, error = (
        _parse_positive_integer(
            request.GET.get(
                "page",
                "1",
            ),
            "page",
        )
    )

    if error is not None:
        return None, error

    page_size, error = (
        _parse_positive_integer(
            request.GET.get(
                "page_size",
                str(
                    DEFAULT_PAGE_SIZE
                ),
            ),
            "page_size",
        )
    )

    if error is not None:
        return None, error

    if page_size > MAX_PAGE_SIZE:
        return (
            None,
            JsonResponse(
                {
                    "status": "error",
                    "message": (
                        "page_size cannot "
                        f"exceed "
                        f"{MAX_PAGE_SIZE}."
                    ),
                },
                status=400,
            ),
        )

    return (
        {
            "search": search,
            "ordering": ordering,
            "page": page,
            "page_size": page_size,
        },
        None,
    )


def _parse_positive_integer(
    raw_value,
    field_name,
):
    try:
        value = int(raw_value)
    except (
        TypeError,
        ValueError,
    ):
        return (
            None,
            _invalid_positive_integer(
                field_name
            ),
        )

    if value < 1:
        return (
            None,
            _invalid_positive_integer(
                field_name
            ),
        )

    return value, None


def _invalid_positive_integer(
    field_name,
):
    return JsonResponse(
        {
            "status": "error",
            "message": (
                f"{field_name} must be "
                "a positive integer."
            ),
        },
        status=400,
    )


def _method_not_allowed(
    allowed_methods,
):
    response = JsonResponse(
        {
            "status": "error",
            "message":
                "Method not allowed.",
        },
        status=405,
    )

    response["Allow"] = ", ".join(
        allowed_methods
    )

    return response