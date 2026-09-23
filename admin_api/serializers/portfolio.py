def serialize_portfolio_summary(
    portfolio,
):
    cover_images = getattr(
        portfolio,
        "cover_images",
        (),
    )

    cover_image = (
        cover_images[0]
        if cover_images
        else None
    )

    return {
        "id": portfolio.pk,
        "name": portfolio.name,
        "slug": portfolio.slug,
        "summary":
            portfolio.summary,
        "category":
            portfolio.category,
        "project_type":
            portfolio.project_type,
        "status":
            portfolio.status,
        "cover_image": (
            serialize_portfolio_image(
                cover_image
            )
            if cover_image
            else None
        ),
        "team_member_count": (
            getattr(
                portfolio,
                "team_member_count",
                0,
            )
        ),
        "project_initiation_date":
            _date_value(
                portfolio
                .project_initiation_date
            ),
        "deadline_date":
            _date_value(
                portfolio.deadline_date
            ),
        "published_at":
            _datetime_value(
                portfolio.published_at
            ),
        "created_at":
            _datetime_value(
                portfolio.created_at
            ),
        "updated_at":
            _datetime_value(
                portfolio.updated_at
            ),
    }


def serialize_portfolio_detail(
    portfolio,
):
    return {
        "id": portfolio.pk,
        "name": portfolio.name,
        "slug": portfolio.slug,
        "summary":
            portfolio.summary,
        "description":
            portfolio.description,
        "category":
            portfolio.category,
        "project_type":
            portfolio.project_type,
        "live_url":
            portfolio.live_url
            or None,
        "figma_url":
            portfolio.figma_url
            or None,
        "project_initiation_date":
            _date_value(
                portfolio
                .project_initiation_date
            ),
        "deadline_date":
            _date_value(
                portfolio.deadline_date
            ),
        "status":
            portfolio.status,
        "published_at":
            _datetime_value(
                portfolio.published_at
            ),
        "team_members": [
            serialize_portfolio_team_member(
                member
            )
            for member
            in portfolio
            .team_members
            .all()
        ],
        "images": [
            serialize_portfolio_image(
                image
            )
            for image
            in portfolio.images.all()
        ],
        "documents": [
            serialize_portfolio_document(
                document
            )
            for document
            in portfolio
            .documents
            .all()
        ],
        "repositories": [
            serialize_portfolio_repository(
                repository
            )
            for repository
            in portfolio
            .repositories
            .all()
        ],
        "created_at":
            _datetime_value(
                portfolio.created_at
            ),
        "updated_at":
            _datetime_value(
                portfolio.updated_at
            ),
    }


def serialize_portfolio_team_member(
    member,
):
    return {
        "id": member.pk,
        "name": member.name,
        "slug": member.slug,
        "position":
            member.position,
        "image":
            _file_url(
                member.image
            ),
    }


def serialize_portfolio_image(
    image,
):
    return {
        "id": image.pk,
        "image":
            _file_url(
                image.image
            ),
        "alt_text":
            image.alt_text,
        "is_cover":
            image.is_cover,
        "position":
            image.position,
        "created_at":
            _datetime_value(
                image.created_at
            ),
        "updated_at":
            _datetime_value(
                image.updated_at
            ),
    }


def serialize_portfolio_document(
    document,
):
    return {
        "id": document.pk,
        "title":
            document.title,
        "url":
            document.url,
        "created_at":
            _datetime_value(
                document.created_at
            ),
        "updated_at":
            _datetime_value(
                document.updated_at
            ),
    }


def serialize_portfolio_repository(
    repository,
):
    return {
        "id": repository.pk,
        "label":
            repository.label,
        "url":
            repository.url,
        "created_at":
            _datetime_value(
                repository.created_at
            ),
        "updated_at":
            _datetime_value(
                repository.updated_at
            ),
    }


def serialize_form_errors(
    form,
):
    return {
        field: [
            str(error)
            for error in errors
        ]
        for field, errors
        in form.errors.items()
    }


def _file_url(
    file_field,
):
    if not file_field:
        return None

    try:
        return file_field.url
    except ValueError:
        return None


def _date_value(value):
    return (
        value.isoformat()
        if value
        else None
    )


def _datetime_value(value):
    return (
        value.isoformat()
        if value
        else None
    )