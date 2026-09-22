from django.core.paginator import (
    Paginator,
)


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class PaginationError(
    ValueError
):
    pass


def paginate_queryset(
    queryset,
    query_params,
):
    page_number = (
        _positive_integer(
            query_params.get(
                "page",
                "1",
            ),
            "page",
        )
    )

    page_size = (
        _positive_integer(
            query_params.get(
                "page_size",
                str(
                    DEFAULT_PAGE_SIZE
                ),
            ),
            "page_size",
        )
    )

    if (
        page_size
        > MAX_PAGE_SIZE
    ):
        raise PaginationError(
            "page_size cannot exceed "
            f"{MAX_PAGE_SIZE}."
        )

    paginator = Paginator(
        queryset,
        page_size,
    )

    page = paginator.get_page(
        page_number
    )

    return (
        page,
        {
            "page": page.number,
            "page_size": page_size,
            "total_items":
                paginator.count,
            "total_pages":
                paginator.num_pages,
            "has_next":
                page.has_next(),
            "has_previous":
                page.has_previous(),
        },
    )


def _positive_integer(
    raw_value,
    field_name,
):
    try:
        value = int(
            raw_value
        )
    except (
        TypeError,
        ValueError,
    ):
        raise PaginationError(
            f"{field_name} must be "
            "a positive integer."
        )

    if value < 1:
        raise PaginationError(
            f"{field_name} must be "
            "a positive integer."
        )

    return value