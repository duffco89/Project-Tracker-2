"""=============================================================
 ~/pjtk2/views/misc_views.py
 Created: 24 Apr 2020 17:48:14

 DESCRIPTION:

  This file contains a number of views that were not associated with
  any one task inparticular.  There is a view to serve static file,
  render and about page, and a simple template view that returns an
  html page describing each of the project milestones.

 A. Cottrill
=============================================================

"""


import mimetypes
import os
from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

# =================================================


def serve_file(request, filename):
    """
    This function is my first attempt at a function used to
    serve/download files.  It works for basic text files, but seems to
    corrupt pdf and ppt files (maybe other binaries too).  It also
    should be updated to include some error trapping just incase the
    file doesn t actully exist.

    from:http://stackoverflow.com/questions/2464888/
    downloading-a-csv-file-in-django?rq=1

    """

    fname = os.path.join(settings.MEDIA_ROOT, filename)

    if os.path.isfile(fname):

        content_type = mimetypes.guess_type(filename)[0]

        filename = os.path.split(filename)[-1]
        wrapper = FileWrapper(open(fname, "rb"))
        response = HttpResponse(wrapper, content_type=content_type)
        response["Content-Disposition"] = "attachment; filename=%s" % os.path.basename(
            fname
        )
        response["Content-Length"] = os.path.getsize(fname)

        return response
    else:
        return render(request, "pjtk2/MissingFile.html", {"filename": filename})


def about_view(request):
    """
    a view to render the about page.
    """
    return render(request, "pjtk2/about.html")


def report_desc_view(request):
    """
    A view to render the html page that describes each of the project
    tracker reporting requirements.
    """
    return render(request, "pjtk2/reporting_milestone_descriptions.html")
