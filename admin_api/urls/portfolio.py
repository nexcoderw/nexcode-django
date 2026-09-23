from django.urls import path

from admin_api.views.portfolio.add import (
    add_portfolio_view,
)
from admin_api.views.portfolio.delete import (
    delete_portfolio_view,
)
from admin_api.views.portfolio.detail import (
    portfolio_detail_view,
)
from admin_api.views.portfolio.document_add import (
    add_portfolio_document_view,
)
from admin_api.views.portfolio.document_delete import (
    delete_portfolio_document_view,
)
from admin_api.views.portfolio.document_update import (
    update_portfolio_document_view,
)
from admin_api.views.portfolio.image_add import (
    add_portfolio_image_view,
)
from admin_api.views.portfolio.image_delete import (
    delete_portfolio_image_view,
)
from admin_api.views.portfolio.image_update import (
    update_portfolio_image_view,
)
from admin_api.views.portfolio.list import (
    list_portfolio_view,
)
from admin_api.views.portfolio.repository_add import (
    add_portfolio_repository_view,
)
from admin_api.views.portfolio.repository_delete import (
    delete_portfolio_repository_view,
)
from admin_api.views.portfolio.repository_update import (
    update_portfolio_repository_view,
)
from admin_api.views.portfolio.update import (
    update_portfolio_view,
)


app_name = "portfolio"


urlpatterns = [
    path(
        "list/",
        list_portfolio_view,
        name="list",
    ),
    path(
        "add/",
        add_portfolio_view,
        name="add",
    ),
    path(
        "detail/<int:portfolio_id>/",
        portfolio_detail_view,
        name="detail",
    ),
    path(
        "update/<int:portfolio_id>/",
        update_portfolio_view,
        name="update",
    ),
    path(
        "delete/<int:portfolio_id>/",
        delete_portfolio_view,
        name="delete",
    ),

    path(
        "image/add/<int:portfolio_id>/",
        add_portfolio_image_view,
        name="image_add",
    ),
    path(
        "image/update/<int:image_id>/",
        update_portfolio_image_view,
        name="image_update",
    ),
    path(
        "image/delete/<int:image_id>/",
        delete_portfolio_image_view,
        name="image_delete",
    ),

    path(
        "document/add/<int:portfolio_id>/",
        add_portfolio_document_view,
        name="document_add",
    ),
    path(
        "document/update/<int:document_id>/",
        update_portfolio_document_view,
        name="document_update",
    ),
    path(
        "document/delete/<int:document_id>/",
        delete_portfolio_document_view,
        name="document_delete",
    ),

    path(
        "repository/add/<int:portfolio_id>/",
        add_portfolio_repository_view,
        name="repository_add",
    ),
    path(
        "repository/update/<int:repository_id>/",
        update_portfolio_repository_view,
        name="repository_update",
    ),
    path(
        "repository/delete/<int:repository_id>/",
        delete_portfolio_repository_view,
        name="repository_delete",
    ),
]