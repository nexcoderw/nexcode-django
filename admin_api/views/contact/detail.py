from admin_api.permissions import (
    nexcode_admin_required,
)
from admin_api.serializers.contact import (
    serialize_admin_contact,
    serialize_contact_reply,
)
from admin_api.views.contact.responses import (
    contact_not_found,
    json_response,
    method_not_allowed,
)
from home.models import Contact


@nexcode_admin_required
def contact_detail_view(
    request,
    contact_id,
):
    if request.method != "GET":
        return method_not_allowed(
            ["GET"]
        )

    contact = (
        Contact.objects.filter(
            pk=contact_id
        )
        .prefetch_related(
            "replies__sent_by"
        )
        .first()
    )

    if contact is None:
        return contact_not_found()

    return json_response(
        {
            "status": "success",
            "data": {
                "contact":
                    serialize_admin_contact(
                        contact
                    ),
                "replies": [
                    serialize_contact_reply(
                        reply
                    )
                    for reply
                    in contact.replies.all()
                ],
            },
        }
    )
