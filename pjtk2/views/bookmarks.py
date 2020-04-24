"""=============================================================
 ~/pjtk2/views/bookmarks.py
 Created: 24 Apr 2020 17:47:32

 DESCRIPTION:

  The views in this file are associated with created and deleting
  bookmarks.

 A. Cottrill
=============================================================

"""


from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from ..models import Project, Bookmark


# =====================
# Bookmark views
@login_required
def bookmark_project(request, slug):
    """
    Modified from Practical Django Projects - pg 189.  Add an entry in
    the bookmarks table for the given user and proejct.
    """
    project = get_object_or_404(Project, slug=slug)
    try:
        Bookmark.objects.get(user__pk=request.user.id, project__slug=project.slug)
    except Bookmark.DoesNotExist:
        Bookmark.objects.create(user=request.user, project=project)
    return HttpResponseRedirect(project.get_absolute_url())


@login_required
def unbookmark_project(request, slug):
    """
    A function to remove a bookmark for a particular user and project.
    """
    project = get_object_or_404(Project, slug=slug)
    if request.method == "POST":
        Bookmark.objects.filter(
            user__pk=request.user.id, project__pk=project.id
        ).delete()
        return HttpResponseRedirect(project.get_absolute_url())
    else:
        return render(
            request, "pjtk2/confirm_bookmark_delete.html", {"project": project}
        )
