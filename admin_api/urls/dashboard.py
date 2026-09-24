from django.urls import path

from admin_api.views.dashboard.overview import (
    dashboard_overview_view,
)


app_name = "dashboard"


urlpatterns = [
    path(
        "overview/",
        dashboard_overview_view,
        name="overview",
    ),
]
