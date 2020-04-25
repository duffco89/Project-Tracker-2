"""=============================================================
 ~/pjtk2/urls/project_images.py
 Created: 25 Apr 2020 17:41:37

 DESCRIPTION:

 These urls are associated wth uploading, sorting and deleting images
 associated with a project.

 A. Cottrill
=============================================================

"""


from django.conf import settings
from django.urls import path, re_path

from pjtk2.views import (
    # images
    project_add_image,
    project_sort_images,
    project_images,
    edit_image,
    delete_image_file,
)

PRJ_CD_REGEX = settings.PRJ_CD_REGEX


urlpatterns = [
    # ==============================
    # images
    re_path(
        (r"project/add_image/" + PRJ_CD_REGEX),
        project_add_image,
        name="project_add_image",
    ),
    re_path((r"project/images/" + PRJ_CD_REGEX), project_images, name="project_images"),
    re_path(
        (r"project/sort_images/" + PRJ_CD_REGEX),
        project_sort_images,
        name="project_sort_images",
    ),
    path("project/edit_image/<int:pk>/", edit_image, name="project_edit_image"),
    path(
        "project/delete_image/<int:pk>/",
        view=delete_image_file,
        name="delete_image_file",
    ),
]
