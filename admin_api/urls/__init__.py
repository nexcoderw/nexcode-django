from django.urls import (
    include,
    path,
)


app_name = "admin_api"


urlpatterns = [
    path(
        "auth/",
        include(
            "admin_api.urls.auth"
        ),
    ),

    path(
        "team/",
        include(
            "admin_api.urls.team"
        ),
    ),

    path(
        "portfolio/",
        include(
            "admin_api.urls.portfolio"
        ),
    ),

    path(
        "client/",
        include(
            "admin_api.urls.client"
        ),
    ),
]