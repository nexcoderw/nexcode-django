def serialize_team_member(team_member):
    return {
        "id": team_member.pk,
        "name": team_member.name,
        "slug": team_member.slug,
        "position": team_member.position,
        "image": _file_url(
            team_member.image
        ),
        "image_png": _file_url(
            team_member.image_png
        ),
        "linkedin": team_member.linkedin,
        "github": team_member.github,
        "created_at": (
            team_member.created_at.isoformat()
        ),
        "updated_at": (
            team_member.updated_at.isoformat()
        ),
    }


def _file_url(file_field):
    if not file_field:
        return None

    try:
        return file_field.url
    except ValueError:
        return None