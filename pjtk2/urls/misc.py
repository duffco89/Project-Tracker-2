"""=============================================================
~/pjtk2/pjtk2/urls/misc.py
 Created: 25 Apr 2020 17:38:43

 DESCRIPTION:

  These url as miscellaneous urls used by the pjtk2 application that
  don't really fit anywhere else.

 A. Cottrill
=============================================================

"""


from django.urls import include, path, re_path

from pjtk2.views import about_view, report_desc_view, serve_file


urlpatterns = [
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
]
