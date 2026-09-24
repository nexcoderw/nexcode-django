from django.urls import path

from admin_api.views.contact.add import (
    add_contact_view,
)


app_name = "contact"


urlpatterns = [
    path(
        "add/",
        add_contact_view,
        name="add",
    ),
]