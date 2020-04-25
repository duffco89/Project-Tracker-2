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
    # project management
    approveprojects,
    approve_project,
    cancel_project,
    uncancel_project,
    signoff_project,
    reopen_project,
    sisterprojects,
    # project CRUD
    new_project,
    copy_project,
    edit_project,
    project_detail,
    report_milestones,
    delete_report,
    report_upload,
    associated_file_upload,
    delete_associated_file,
    # bookmarking
    bookmark_project,
    unbookmark_project,
    # images
    project_add_image,
    project_sort_images,
    project_images,
    edit_image,
    delete_image_file,
    # misc
    about_view,
    report_desc_view,
    serve_file,
)


PRJ_CD_REGEX = r"(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$"

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

urlpatterns += [
    # ==============================
    # Project Management
    path("approveprojects/", approveprojects, name="ApproveProjects"),
    re_path(
        (r"^approve_project/" + PRJ_CD_REGEX), approve_project, name="approve_project"
    ),
    # url((r'^unapprove_project/'
    #      PRJ_CD_REGEX),
    #    'unapprove_project', name='unapprove_project'),
    re_path(
        (r"^cancel_project/" + PRJ_CD_REGEX), cancel_project, name="cancel_project"
    ),
    re_path(
        (r"^uncancel_project/" + PRJ_CD_REGEX),
        uncancel_project,
        name="uncancel_project",
    ),
    re_path(
        (r"^signoff_project/" + PRJ_CD_REGEX), signoff_project, name="signoff_project"
    ),
    re_path(
        (r"^reopen_project/" + PRJ_CD_REGEX), reopen_project, name="reopen_project"
    ),
    re_path(
        (r"^sisterprojects/" + PRJ_CD_REGEX), sisterprojects, name="SisterProjects"
    ),
]

urlpatterns += [
    # ==============================
    #  Project CRUD
    path("newproject/", new_project, name="NewProject"),
    re_path((r"^copyproject/" + PRJ_CD_REGEX), copy_project, name="CopyProject"),
    re_path((r"^editproject/" + PRJ_CD_REGEX), edit_project, name="EditProject"),
    re_path((r"^projectdetail/" + PRJ_CD_REGEX), project_detail, name="project_detail"),
    # ==============================
    # Reports and milestones
    re_path(r"^reports/" + PRJ_CD_REGEX, report_milestones, name="Reports"),
    #    url(r'^reportformset/', 'report_formset', name='ReportFormSet'),
    #    url((r'^updateassignments/'
    #            PRJ_CD_REGEX),
    #        'update_assignments', name='UpdateAssignments'),
    # url(r'^(?P<slug>[A-Z]{3}_[A-Z]{2}\d{2}_([A-Z]|\d){3})/$',
    #       'project_milestones', name='ProjectMilestones'),
    re_path(
        (
            r"^delete_report/"
            r"(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/"
            r"(?P<pk>\d+)/$"
        ),
        view=delete_report,
        name="delete_report",
    ),
    re_path((r"^reportupload/" + PRJ_CD_REGEX), report_upload, name="ReportUpload"),
    re_path(
        (r"^associatedfileupload/" + PRJ_CD_REGEX),
        associated_file_upload,
        name="associated_file_upload",
    ),
    path(
        "delete_associated_file/<int:id>/",
        view=delete_associated_file,
        name="delete_associated_file",
    ),
]

urlpatterns += [
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
    # images
    path("project/edit_image/<int:pk>/", edit_image, name="project_edit_image"),
    path(
        "project/delete_image/<int:pk>/",
        view=delete_image_file,
        name="delete_image_file",
    ),
]

urlpatterns += [
    # ==============================
    #  MISC Views
    # url(r'^uploadlist/$', 'uploadlist', name='UploadList'),
    path("api/", include("pjtk2.api.urls", namespace="api")),
    # this function is used to download reports and files from project pages
    re_path(r"^serve_file/(?P<filename>.+)$", serve_file, name="serve_file"),
    # path("serve_file/<str:filename>/", serve_file, name="serve_file"),
    path("about/", about_view, name="about_view"),
    path("report_descriptions/", report_desc_view, name="report_desc_view"),
    # ==============================
    # bookmarking
    re_path(
        (r"^bookmarkproject/" + PRJ_CD_REGEX), bookmark_project, name="Bookmark_Project"
    ),
    re_path(
        (r"^unbookmarkproject/" + PRJ_CD_REGEX),
        unbookmark_project,
        name="Unbookmark_Project",
    ),
]
