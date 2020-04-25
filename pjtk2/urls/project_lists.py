"""=============================================================
 ~/pjtk2/urls/project_lists.py
 Created: 25 Apr 2020 17:42:31

 DESCRIPTION:

 The urls in this file return lists of projects - by user, region of
 interest, tag, ect.

 A. Cottrill
=============================================================

"""


from django.urls import include, path, re_path

from pjtk2.views import (
    # list of projects
    ProjectSearch,
    project_list,
    user_project_list,
    approved_projects_list,
    taggedprojects,
    project_tag_list,
    my_projects,
    employee_projects,
    find_projects_roi_view,
)

urlpatterns = [
    # ==============================
    # Project Lists
    path("projects/approved/", approved_projects_list, name="ApprovedProjectsList"),
    path("projects/<str:username>/", user_project_list, name="user_project_list"),
    path("projects/", project_list, name="ProjectList"),
    path("search/", ProjectSearch.as_view(), name="project_search"),
    path("myprojects/", my_projects, name="MyProjects"),
    path(
        "employeeprojects/<str:employee_name>/",
        employee_projects,
        name="EmployeeProjects",
    ),
    # tagging/keywords
    path("taggedprojects/<str:tag>/", taggedprojects, name="TaggedProjects"),
    path("tags/", project_tag_list, name="project_tag_list"),
    # projects by region of interest:
    path("projects_roi/", find_projects_roi_view, name="find_projects_roi"),
]
