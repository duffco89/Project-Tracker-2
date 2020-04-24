"""=============================================================
 ~/pjtk2/views/project_images.py
 Created: 24 Apr 2020 17:52:51

 DESCRIPTION:

The views in this file are associated with uploading, editing,
deleting and re-arranging the files associated with a project.

 A. Cottrill
=============================================================

"""


from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import resolve, Resolver404
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from ..models import Project, ProjectImage

from ..forms import ProjectImageForm, EditImageForm

from ..utils.helpers import can_edit


@login_required
def project_add_image(request, slug):
    """

    Arguments:
    - `request`:
    - `slug`:
    """

    project = get_object_or_404(Project, slug=slug)

    if can_edit(request.user, project) is False:
        return HttpResponseRedirect(project.get_absolute_url())

    form = ProjectImageForm()

    if request.method == "POST":
        form = ProjectImageForm(request.POST, request.FILES)
        form.project = project
        if form.is_valid():
            image = form.save(commit=False)
            image.order = project.images.count() + 1
            image.project = project
            image.save()
            # if we subitted with the save button, return to the
            # project detail, otherwise return to the form (save and
            # add another)
            if "save" in request.POST:
                return HttpResponseRedirect(project.get_absolute_url())
            else:
                # create an empty form to add another image.
                form = ProjectImageForm()

    return render(
        request, "pjtk2/project_image_upload.html", {"form": form, "object": project}
    )


@login_required
def edit_image(request, pk):
    """

    Arguments:
    - `request`:
    - `slug`:
    """

    image = get_object_or_404(ProjectImage, pk=pk)
    project = image.project

    if can_edit(request.user, project) is False:
        return HttpResponseRedirect(project.get_absolute_url())

    form = EditImageForm(instance=image)

    if request.method == "POST":
        form = EditImageForm(request.POST, instance=image)
        if form.is_valid():
            form.save()
            report_cnt = settings.MAX_REPORT_IMG_COUNT
            # this should be moved to project model:
            # project.trim_report_images(MAX_REPORT_IMG_COUNT)
            extra_images = project.images.filter(report=True).order_by("order")[
                report_cnt:
            ]
            if extra_images:
                for img in extra_images:
                    img.report = False
                    img.save()

            url = request.POST.get("next")
            try:
                resolve(url)
                return HttpResponseRedirect(url)
            except Resolver404:
                return HttpResponseRedirect(project.get_absolute_url())

    return render(
        request,
        "pjtk2/edit_image.html",
        {"form": form, "image": image, "project": project},
    )


@login_required
def project_images(request, slug):
    """
    Display all of the images associated with a project in a form that
    provides drag-and-drop sorting and double-click editing.
    """
    project = get_object_or_404(Project, slug=slug)

    if can_edit(request.user, project) is False:
        return HttpResponseRedirect(project.get_absolute_url())

    return render(request, "pjtk2/project_sort_images.html", {"project": project})


@login_required
@csrf_exempt
def project_sort_images(request, slug):
    """
    This view is called by jQuery imbeded in project_sort_images.html
    and re-orders the images based on the order that they appear in
    the drag-and-drop interface.
    """
    for index, image_pk in enumerate(request.POST.getlist("image[]")):
        image = ProjectImage.objects.filter(id=int(str(image_pk))).first()
        if image:
            image.order = index
            image.save()
    return HttpResponse("")


@login_required
def delete_image_file(request, pk):
    """
    This view deletes an image

    If this is a get request, redirect to a confirmation page.  If it
    is a post, delete the associated image and return to the project
    detail page.

    Arguments:
    - `request`:
    - `slug`:
    - `pk`:

    """
    image = get_object_or_404(ProjectImage, pk=pk)
    project = image.project

    if can_edit(request.user, project) is False:
        return HttpResponseRedirect(project.get_absolute_url())

    if request.method == "POST":
        image.delete()
        return HttpResponseRedirect(project.get_absolute_url())
    else:
        return render(
            request,
            "pjtk2/confirm_image_delete.html",
            {"image": image, "project": project},
        )
