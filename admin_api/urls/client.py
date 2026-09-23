from django.urls import path

from admin_api.views.client.add import (
    add_client_view,
)
from admin_api.views.client.delete import (
    delete_client_view,
)
from admin_api.views.client.detail import (
    client_detail_view,
)
from admin_api.views.client.list import (
    list_client_view,
)
from admin_api.views.client.update import (
    update_client_view,
)


app_name = "client"


urlpatterns = [
    path(
        "list/",
        list_client_view,
        name="list",
    ),
    path(
        "add/",
        add_client_view,
        name="add",
    ),
    path(
        "detail/<int:client_id>/",
        client_detail_view,
        name="detail",
    ),
    path(
        "update/<int:client_id>/",
        update_client_view,
        name="update",
    ),
    path(
        "delete/<int:client_id>/",
        delete_client_view,
        name="delete",
    ),
]