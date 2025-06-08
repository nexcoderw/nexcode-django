from controller.views import *
from django.conf import settings
from django.urls import path, re_path
from django.conf.urls.static import static

app_name = 'admin'

urlpatterns = [
    path('', signIn, name="signIn"),

    path('dashboard/', dashboard, name="dashboard"),

    path('clients/', clients, name="clients"),
    path('client/id/', clientDetails, name="clientDetails"),
    path('client/id/update/', updateClient, name="updateClient"),
    path('client/id/delete/', deleteClient, name="deleteClient"),

    path('team/', team, name="team"),
    path('team/id/', memberDetals, name="memberDetals"),
    path('team/id/update/', updateMember, name="updateMember"),
    path('team/id/delete/', deleteMember, name="deleteMember"),

    path('projects/', projects, name="projects"),
    path('project/id/', projectDetails, name="projectDetails"),
    path('project/id/update/', updateProject, name="updateProject"),
    path('project/id/delete/', deleteProject, name="deleteProject"),

    path('blogs/', blogs, name="blogs"),
    path('blog/id/', blogDetails, name="blogDetails"),
    path('blog/id/update/', updateBlog, name="updateBlog"),
    path('blog/id/delete/', deleteBlog, name="deleteBlog"),

    path('testimonies/', testimonies, name="testimonies"),
    path('testimont/id/', testimonyDetails, name="testimonyDetails"),
    path('testimont/id/update/', updateTestimony, name="updateTestimony"),
    path('testimont/id/delete/', deleteTestimony, name="deleteTestimony"),

    path('contacts/', contacts, name="contacts"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
