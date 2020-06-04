"""=============================================================
 ~/pjtk2/urls/project_management.py
 Created: 25 Apr 2020 17:43:26

 DESCRIPTION:

  The urls in this file are generally used by managers to manage
  projects - approve, cancel, and re-open.

 A. Cottrill
=============================================================

"""


from django.conf import settings
from django.urls import include, path, re_path

from pjtk2.views import (
    # project management
    approveprojects,
    approve_project,
    cancel_project,
    uncancel_project,
    signoff_project,
    reopen_project,
    sisterprojects,
)


PRJ_CD_REGEX = settings.PRJ_CD_REGEX


urlpatterns = [
    # ==============================
    # Project Management
    path("approve_projects/", approveprojects, name="ApproveProjects"),
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
        (r"^sister_projects/" + PRJ_CD_REGEX), sisterprojects, name="SisterProjects"
    ),
]
