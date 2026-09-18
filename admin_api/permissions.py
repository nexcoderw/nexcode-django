from functools import wraps

from django.http import JsonResponse

from admin_api.constants import NEXCODE_ADMIN_GROUP_NAME


def is_nexcode_admin(user):
    """Return whether a user may access the NEXCODE administration API."""
    if not getattr(user, "is_authenticated", False):
        return False

    if not getattr(user, "is_active", False):
        return False

    return user.groups.filter(
        name=NEXCODE_ADMIN_GROUP_NAME,
    ).exists()


def nexcode_admin_required(view_func):
    """Require an authenticated NEXCODE administrator."""

    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Authentication required.",
                },
                status=401,
            )

        if not is_nexcode_admin(request.user):
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Administrator access required.",
                },
                status=403,
            )

        return view_func(
            request,
            *args,
            **kwargs,
        )

    return wrapped_view