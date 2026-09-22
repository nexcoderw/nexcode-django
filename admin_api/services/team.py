from django.db import transaction

from home.models import Team


TEXT_FIELDS = (
    "name",
    "position",
    "linkedin",
    "github",
)


def create_team_member(
    cleaned_data,
):
    with transaction.atomic():
        return Team.objects.create(
            name=cleaned_data[
                "name"
            ],
            position=cleaned_data[
                "position"
            ],
            image=cleaned_data.get(
                "image"
            ),
            image_png=cleaned_data.get(
                "image_png"
            ),
            linkedin=(
                cleaned_data.get(
                    "linkedin"
                )
                or None
            ),
            github=(
                cleaned_data.get(
                    "github"
                )
                or None
            ),
        )


def update_team_member(
    team_member,
    form,
):
    data = form.cleaned_data

    with transaction.atomic():
        for field_name in TEXT_FIELDS:
            if field_name not in form.data:
                continue

            value = data.get(
                field_name
            )

            setattr(
                team_member,
                field_name,
                value or None,
            )

        if "image" in form.files:
            team_member.image = (
                data["image"]
            )

        if (
            "image_png"
            in form.files
        ):
            team_member.image_png = (
                data["image_png"]
            )

        if data.get(
            "remove_image"
        ):
            team_member.image = None

        if data.get(
            "remove_image_png"
        ):
            team_member.image_png = (
                None
            )

        team_member.save()

    return team_member


def delete_team_member(
    team_member,
):
    with transaction.atomic():
        team_member.delete()