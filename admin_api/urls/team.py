from django.urls import path

from admin_api.views import team


app_name = "team"


urlpatterns = [
    path(
        "",
        team.team_collection_view,
        name="collection",
    ),
    path(
        "<int:team_id>/",
        team.team_item_view,
        name="item",
    ),
]