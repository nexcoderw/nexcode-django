from django.urls import path

from admin_api.views.contact.add import (
    add_contact_view,
)
from admin_api.views.contact.detail import (
    contact_detail_view,
)
from admin_api.views.contact.list import (
    list_contact_view,
)
from admin_api.views.contact.reply import (
    reply_contact_view,
)


app_name = "contact"


urlpatterns = [
    path(
        "add/",
        add_contact_view,
        name="add",
    ),
    path(
        "list/",
        list_contact_view,
        name="list",
    ),
    path(
        "detail/<int:contact_id>/",
        contact_detail_view,
        name="detail",
    ),
    path(
        "reply/<int:contact_id>/",
        reply_contact_view,
        name="reply",
    ),
]
