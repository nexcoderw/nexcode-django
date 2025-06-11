from controller.views import *
from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

app_name = "controller"

urlpatterns = [
    path("", signIn, name="signIn"),
    path("logout/", signOut, name="signOut"),

    # ----------Dashboard----------
    path("dashboard/", dashboard, name="dashboard"),

    # ---------- Clients ----------
    path("clients/", clients, name="clients"),
    path("client/add/", addClient, name="addClient"),
    path("client/<int:id>/", clientDetails, name="clientDetails"),
    path("client/<int:id>/update/", updateClient, name="updateClient"),
    path("client/<int:id>/delete/", deleteClient, name="deleteClient"),

    # ---------- Team ----------
    path("team/", team, name="team"),
    path("team/add/", addMember, name="addMember"),
    path("team/<int:id>/", memberDetails, name="memberDetails"),
    path("team/<int:id>/update/", updateMember, name="updateMember"),
    path("team/<int:id>/delete/", deleteMember, name="deleteMember"),

    # ---------- Projects ----------
    path("projects/", projects, name="projects"),
    path("project/add/", addProject, name="addProject"),
    path("project/<int:id>/", projectDetails, name="projectDetails"),
    path("project/<int:id>/update/", updateProject, name="updateProject"),
    path("project/<int:id>/delete/", deleteProject, name="deleteProject"),

    # ---------- Blogs ----------
    path("blogs/", blogs, name="blogs"),
    path("blog/add/", addBlog, name="addBlog"),
    path("blog/<int:id>/", blogDetails, name="blogDetails"),
    path("blog/<int:id>/update/", updateBlog, name="updateBlog"),
    path("blog/<int:id>/delete/", deleteBlog, name="deleteBlog"),

    # ---------- Testimonies ----------
    path("testimonies/", testimonies, name="testimonies"),
    path("testimony/add/", addTestimony, name="addTestimony"),
    path("testimont/<int:id>/", testimonyDetails, name="testimonyDetails"),
    path("testimont/<int:id>/update/", updateTestimony, name="updateTestimony"),
    path("testimont/<int:id>/delete/", deleteTestimony, name="deleteTestimony"),

    # ---------- Contacts ----------
    path("contacts/", contacts, name="contacts"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
