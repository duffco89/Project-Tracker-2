"""=============================================================
~/pjtk2/urls/bookmarks.py
 Created: 25 Apr 2020 17:37:45

 DESCRIPTION:

  These are the urls associated with bookmarking and unbookmarking
  projects.

 A. Cottrill
=============================================================

"""


from django.conf import settings
from django.urls import include, path, re_path

from pjtk2.views import bookmark_project, unbookmark_project


PRJ_CD_REGEX = settings.PRJ_CD_REGEX


urlpatterns = [
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
