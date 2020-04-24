"""=============================================================
 ~/pjtk2/views/management.py

 Created: 24 Apr 2020 17:50:22

 DESCRIPTION:

  This file contains all of the views associated with project
  management.  Most (but not all) require the logged in user to be a
  manager or administrator.  This includes things like approving and
  cancelling projects, editing reporting requirements, etc.

 A. Cottrill
=============================================================

"""


# E1101 - Class 'whatever' has no 'something' member
# E1120 - No value passed for parameter 'cls' in function call
# pylint: disable=E1101, E1120


import datetime
import pytz

import collections

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.forms import formset_factory
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from ..models import Project, ProjectMilestones, Milestone, Employee, Bookmark

from ..forms import ApproveProjectsForm, ReportsForm, NoticesForm, SisterProjectsForm


from ..utils.helpers import (
    is_manager,
    group_required,
    make_possessive,
    get_messages_dict,
    my_messages,
    get_minions,
    get_sisters_dict,
)


# ==========================
#      Managers


@login_required
# @permission_required('Project.can_change_Approved')
def approveprojects(request):
    """
    Areate a list of projects, project names and an
    approved/unapproved checkbox widget.
    """

    if is_manager(request.user) is False:
        return HttpResponseRedirect(reverse("ApprovedProjectsList"))

    project_formset = modelformset_factory(
        model=Project, form=ApproveProjectsForm, extra=0
    )

    # TODO - test that signed off and unactive projects are not included.
    # TODO - test that projects in the future are included in this year
    # thisyears = Project.this_year.all().filter(SignOff=False)
    # lastyears = Project.last_year.all().filter(SignOff=False)
    thisyears = Project.this_year.all()
    lastyears = Project.last_year.all()

    year = datetime.datetime.now().year

    if thisyears.count() == 0:
        this_year_empty = True
    else:
        this_year_empty = False

    if lastyears.count() == 0:
        last_year_empty = True
    else:
        last_year_empty = False

    if request.method == "POST":
        if request.POST["form-type"] == u"thisyear":
            thisyearsformset = project_formset(
                request.POST, queryset=thisyears, prefix="thisyear"
            )
            lastyearsformset = project_formset(queryset=lastyears, prefix="lastyear")

        elif request.POST["form-type"] == u"lastyear":
            lastyearsformset = project_formset(
                request.POST, queryset=lastyears, prefix="lastyear"
            )
            thisyearsformset = project_formset(queryset=thisyears, prefix="thisyear")
        if thisyearsformset.is_valid():
            thisyearsformset.save()
            return HttpResponseRedirect(reverse("ApprovedProjectsList"))
        elif lastyearsformset.is_valid():
            lastyearsformset.save()
            return HttpResponseRedirect(reverse("ApprovedProjectsList"))
        else:
            return render(
                request,
                "pjtk2/ApproveProjects.html",
                {
                    "year": year,
                    "thisYearEmpty": this_year_empty,
                    "lastYearEmpty": last_year_empty,
                    "thisyearsformset": thisyearsformset,
                    "lastyearsformset": lastyearsformset,
                },
            )

    else:
        thisyearsformset = project_formset(queryset=thisyears, prefix="thisyear")
        lastyearsformset = project_formset(queryset=lastyears, prefix="lastyear")

    return render(
        request,
        "pjtk2/ApproveProjects.html",
        {
            "year": year,
            "thisYearEmpty": this_year_empty,
            "lastYearEmpty": last_year_empty,
            "thisyearsformset": thisyearsformset,
            "lastyearsformset": lastyearsformset,
        },
    )


@login_required
@group_required("manager")
def approve_project(request, slug):
    """
    A quick little view that will allow managers to approve projects
    from the project detail page.
    """

    project = get_object_or_404(Project, slug=slug)
    project.approve()
    project.save()
    return HttpResponseRedirect(project.get_absolute_url())


@login_required
@group_required("manager")
def unapprove_project(request, slug):
    """
    A quick little view that will allow managers to unapprove projects
    from the project detail page.
    """

    project = Project.objects.get(slug=slug)
    project.unapprove()
    project.save()
    return HttpResponseRedirect(project.get_absolute_url())


@login_required
def cancel_project(request, slug):
    """
    A view that will allow managers to cancel projects
    from the project detail page. Users who are not managers are
    re-directed to the project detail page without doing anything.

    In order to facilitate messaging and model managers, a cancelled
    milestone needs to be created in addition to updating dedicated
    fields of project objects.

    In order to implement messaging associated with the cancellation
    of a project, 'Cancelled' must be a milestone (a milestone and a
    project are required using current messaging architector.)

    """

    project = get_object_or_404(Project, slug=slug)

    if is_manager(request.user):
        cancelled_ms = Milestone.objects.get(label="Cancelled")
        project_cancelled, created = ProjectMilestones.objects.get_or_create(
            project=project, milestone=cancelled_ms
        )
        now = datetime.datetime.now(pytz.utc)
        project_cancelled.completed = now
        project_cancelled.save()
        # any outstanding task will not longer be required:
        # remaining_ms = ProjectMilestones.objects.filter(project=project,
        #                                                 required=True,
        #                                                 completed__isnull=True).update(required=False)
        # keep track of who cancelled the project
        project.cancelled_by = request.user
        project.cancelled = True
        project.save()
    return HttpResponseRedirect(project.get_absolute_url())


@login_required
def uncancel_project(request, slug):
    """
    A view to re-activate a cancelled project.
    """

    project = get_object_or_404(Project, slug=slug)
    cancelled_ms = get_object_or_404(Milestone, label="Cancelled")
    project_cancelled = get_object_or_404(
        ProjectMilestones, project=project, milestone=cancelled_ms
    )
    if is_manager(request.user):
        project_cancelled.completed = None
        project_cancelled.save()
        project.cancelled_by = None
        project.cancelled = False
        project.save()
    return HttpResponseRedirect(project.get_absolute_url())


@login_required
def signoff_project(request, slug):
    """
    A quick little view that will allow managers to signoff projects
    from the project detail page.
    """

    user = User.objects.get(username__exact=request.user)
    project = get_object_or_404(Project, slug=slug)
    if is_manager(user):
        project.signoff(user)
    return HttpResponseRedirect(project.get_absolute_url())


@login_required
def reopen_project(request, slug):
    """
    A quick little view that will allow managers to reopen projects
    from the project detail page so that reports can be uploaded or
    entries edited.
    """

    user = User.objects.get(username__exact=request.user)
    project = get_object_or_404(Project, slug=slug)
    if is_manager(user):
        project.reopen()
    return HttpResponseRedirect(project.get_absolute_url())


@login_required
@group_required("manager")
def report_milestones(request, slug):
    """
    This function will render a form of requested reporting
    requirements for each project.  Used by managers to update
    reporting requirements for each project.
    """

    project = Project.objects.get(slug=slug)
    reports = project.get_milestone_dicts()

    if request.method == "POST":
        new_report = request.POST.get("new_report", None)
        new_milestone = request.POST.get("new_milestone", None)
        if new_report or new_milestone:
            if new_report:
                new_report = new_report.title()
                # verify that this reporting requirement doesn't already exist
                # then add it to the reporting requirements
                try:
                    Milestone.objects.get_or_create(label=new_report, report=True)
                except Milestone.DoesNotExist:
                    pass
            else:
                new_milestone = new_milestone.title()
                # verify that this reporting requirement doesn't already exist
                # then add it to the reporting requirements
                try:
                    Milestone.objects.get_or_create(label=new_milestone, report=False)
                except Milestone.DoesNotExist:
                    pass

            # now redirect back to the update reports form for this project
            return HttpResponseRedirect(reverse("Reports", args=(project.slug,)))

        else:
            milestones = ReportsForm(
                request.POST, project=project, reports=reports, what="Milestones"
            )
            core = ReportsForm(request.POST, project=project, reports=reports)
            custom = ReportsForm(
                request.POST, project=project, reports=reports, what="Custom"
            )

            if core.is_valid() and custom.is_valid() and milestones.is_valid():
                core.save()
                custom.save()
                milestones.save()
                next = request.POST.get("next", "/")
                return HttpResponseRedirect(next)
                # return HttpResponseRedirect(project.get_absolute_url())
    else:
        milestones = ReportsForm(project=project, reports=reports, what="Milestones")
        core = ReportsForm(project=project, reports=reports)
        custom = ReportsForm(project=project, reports=reports, what="Custom")

    return render(
        request,
        "pjtk2/reportform.html",
        {"Milestones": milestones, "Core": core, "Custom": custom, "project": project},
    )


@login_required
def my_projects(request):
    """
    Gather all of the things a user needs and render them on a single
    page.
    """
    # TODO - write more tests to verify this works as expected.
    bookmarks = Bookmark.objects.filter(user__pk=request.user.id)

    user = User.objects.get(username__exact=request.user)

    milestones = Milestone.objects.filter(category="Core").order_by("order").all()

    milestone_dict = collections.OrderedDict()
    for ms in milestones:
        key = ms.label_abbrev.lower().replace(" ", "-")
        value = {
            "label": ms.label_abbrev,
            "type": "report" if ms.report else "milestone",
        }
        milestone_dict[key] = value

    milestone_dict["custom"] = {"label": "Add. Report(s)", "type": "report"}

    # make sure that the user exists - otherwise redirect them to a
    # help page
    try:
        myself = Employee.objects.get(user=user)
    except:
        msg = """Your employee profile does not appear to be propery
                 configured.\nPlease contact the site administrators."""
        # messages.error(request, msg)
        raise Http404(msg)

    employees = get_minions(myself)
    employees = [x.user.username for x in employees]

    boss = False
    if len(employees) > 1:
        boss = True

    # get the submitted, approved and completed projects from the last five years
    this_year = datetime.datetime.now(pytz.utc).year
    submitted = (
        Project.objects.submitted()
        .select_related("project_type", "prj_ldr")
        .filter(owner__username__in=employees)
        .filter(year__gte=this_year - 5)
    )
    approved = (
        Project.objects.approved()
        .select_related("project_type", "prj_ldr")
        .filter(owner__username__in=employees)
        .filter(year__gte=this_year - 5)
    )
    cancelled = (
        Project.objects.cancelled()
        .select_related("project_type", "prj_ldr")
        .filter(owner__username__in=employees)
        .filter(year__gte=this_year - 5)
    )
    complete = (
        Project.objects.completed()
        .select_related("project_type", "prj_ldr")
        .filter(owner__username__in=employees)
        .filter(year__gte=this_year - 15)
    )

    notices = get_messages_dict(my_messages(user))
    notices_count = len(notices)

    formset = formset_factory(NoticesForm, extra=0)

    if request.method == "POST":
        notices_formset = formset(request.POST, initial=notices)
        if notices_formset.is_valid():
            for form in notices_formset:
                form.save()
            redirect_url = reverse("MyProjects") + "#notices"
            return HttpResponseRedirect(redirect_url)
    else:
        notices_formset = formset(initial=notices)

    template_name = "pjtk2/my_projects.html"

    return render(
        request,
        template_name,
        {
            "bookmarks": bookmarks,
            "formset": notices_formset,
            "complete": complete,
            "approved": approved,
            "cancelled": cancelled,
            "submitted": submitted,
            "boss": boss,
            "notices_count": notices_count,
            "milestones": milestone_dict,
        },
    )


@login_required
def employee_projects(request, employee_name):
    """
    A view accessible only by managers that presents the projects and
    milestone status of projects associated with a specific employee.
    Essentially allows managers to filter their projects view.
    """
    # get the employee user object
    my_employee = get_object_or_404(User, username=employee_name)
    user = User.objects.get(username__exact=request.user)

    # if I am not a manager or in the list of supervisors associated
    # with this employee, return me to my projects page
    if is_manager(user) is False:
        redirect_url = reverse("MyProjects")
        return HttpResponseRedirect(redirect_url)

    # if I am the employees supervisor - get their projects and
    # associated milestones:

    milestones = Milestone.objects.filter(category="Core").order_by("order").all()

    milestone_dict = collections.OrderedDict()
    for ms in milestones:
        key = ms.label_abbrev.lower().replace(" ", "-")
        value = {
            "label": ms.label_abbrev,
            "type": "report" if ms.report else "milestone",
        }
        milestone_dict[key] = value

    milestone_dict["custom"] = {"label": "Add. Report(s)", "type": "report"}

    # core_reports = Milestone.objects.filter(category='Core', report=True)

    # get the submitted, approved and completed projects from the last five years
    this_year = datetime.datetime.now(pytz.utc).year
    submitted = (
        Project.objects.submitted()
        .filter(owner__username=my_employee)
        .filter(year__gte=this_year - 5)
        .select_related("project_type", "prj_ldr")
    )
    approved = (
        Project.objects.approved()
        .filter(owner__username=my_employee)
        .filter(year__gte=this_year - 5)
        .select_related("project_type", "prj_ldr")
    )
    cancelled = (
        Project.objects.cancelled()
        .filter(owner__username=my_employee)
        .filter(year__gte=this_year - 5)
        .select_related("project_type", "prj_ldr")
    )
    complete = (
        Project.objects.completed()
        .filter(owner__username=my_employee)
        .filter(year__gte=this_year - 15)
        .select_related("project_type", "prj_ldr")
    )

    template_name = "pjtk2/employee_projects.html"

    # create a label that will be the possessive form of the employees
    # first and last name
    label = " ".join([my_employee.first_name, my_employee.last_name])

    label = make_possessive(label)

    return render(
        request,
        template_name,
        {
            "employee": my_employee,
            "label": label,
            "complete": complete,
            "approved": approved,
            "cancelled": cancelled,
            "submitted": submitted,
            "milestones": milestone_dict,
            "edit": True,
        },
    )


def sisterprojects(request, slug):
    """
    Render a form that can be used to create groupings of sister
    projects.  Only approved projects in the same year, and of the
    same project type will be presented.  existing sister projects
    will be checked off.  When the form is submitted the sibling
    relationships will be updated according to the values in the
    sister of each returned form.
    """

    project = get_object_or_404(Project, slug=slug)
    initial = get_sisters_dict(slug)
    empty = True if len(initial) == 0 else False

    sister_formset = formset_factory(SisterProjectsForm, extra=0)

    if request.method == "POST":
        formset = sister_formset(request.POST, request.FILES, initial=initial)
        if formset.is_valid():
            # see if any checkboxes have changed
            cleandata = [x.cleaned_data["sister"] for x in formset]
            init = [x.initial["sister"] for x in formset]
            # if cleandata==init, there is nothing to do
            if cleandata != init:
                # if all cleandata==False then remove this project from this
                # family
                if all(x is False for x in cleandata):
                    project.disown()
                else:
                    for form in formset:
                        form.save(parentslug=slug)
            return HttpResponseRedirect(project.get_absolute_url())
    else:
        formset = sister_formset(initial=initial)
    return render(
        request,
        "pjtk2/SisterProjects.html",
        {"formset": formset, "project": project, "empty": empty},
    )
