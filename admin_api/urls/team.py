from django.urls import path

from admin_api.views import team


app_name = "team"


urlpatterns = [
    path(
        "",
        team.team_list_view,
        name="list",
    ),
    path(
        "<int:team_id>/",
        team.team_detail_view,
        name="detail",
    ),
]