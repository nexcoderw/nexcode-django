from django.urls import path

from admin_api.views.team.add import (
    add_team_view,
)
from admin_api.views.team.delete import (
    delete_team_view,
)
from admin_api.views.team.detail import (
    team_detail_view,
)
from admin_api.views.team.list import (
    list_team_view,
)
from admin_api.views.team.update import (
    update_team_view,
)


app_name = "team"


urlpatterns = [
    path(
        "list/",
        list_team_view,
        name="list",
    ),
    path(
        "add/",
        add_team_view,
        name="add",
    ),
    path(
        "detail/<int:team_id>/",
        team_detail_view,
        name="detail",
    ),
    path(
        "update/<int:team_id>/",
        update_team_view,
        name="update",
    ),
    path(
        "delete/<int:team_id>/",
        delete_team_view,
        name="delete",
    ),
]