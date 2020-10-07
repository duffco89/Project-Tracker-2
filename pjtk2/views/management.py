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

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory, formset_factory
from django.forms import formset_factory
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from ..models import Project, ProjectMilestones, Milestone, Employee, Bookmark

from ..forms import (
    ApproveProjectsForm,
    ReportsForm,
    NoticesForm,
    SisterProjectsForm,
    ApproveProjectsForm2,
)

from ..utils.helpers import (
    is_manager,
    # group_required,
    make_possessive,
    get_messages_dict,
    get_approve_project_dict,
    my_messages,
    get_minions,
    get_sisters_dict,
    make_proj_ms_dict,
)

User = get_user_model()


def get_proj_ms(project_ids, milestones):
    """

    Arguments:
    - `project_ids`:
    """

    project_milestones = (
        ProjectMilestones.objects.select_related("project", "milestone")
        # .exclude(
        #    milestone__label__in=["Approved", "Submitted", "Cancelled", "Sign off"]
        # )
        .filter(milestone__in=milestones)
        .filter(project__pk__in=project_ids)
        .prefetch_related("project__project_type", "project__prj_ldr")
        .order_by("-project__year", "project__prj_cd", "milestone__order")
        .values(
            "project__prj_cd",
            "project__prj_nm",
            "project__year",
            "project__slug",
            "project__prj_ldr__first_name",
            "project__prj_ldr__last_name",
            "project__prj_ldr__username",
            "project__project_type__project_type",
            "milestone__category",
            "milestone__report",
            "milestone__label",
            "required",
            "completed",
        )
    )

    return project_milestones


# ==========================
#      Managers


def get_project_filters(this_year, last_year):
    """Return a dictionary containing the unique values for lake, project
    leader and project type from the list of project to be approved this
    and those from last year.

    Arguments:
    - `projects`:

    """

    values = {}
    values["lakes"] = set(
        [x["lake"] for x in this_year] + [x["lake"] for x in last_year]
    )

    # project leads are a little harder because they should be sorted.
    project_leads = list(
        set(
            [x["prj_ldr_label"] for x in this_year]
            + [x["prj_ldr_label"] for x in last_year]
        )
    )
    project_leads.sort()
    values["project_leader"] = project_leads

    values["project_types"] = set(
        [x["project_type"] for x in this_year] + [x["project_type"] for x in last_year]
    )

    return values


@login_required
# @permission_required('Project.can_change_Approved')
def approveprojects2(request):
    """Create a list of projects, project names and an approved/unapproved
    checkbox widget.  This version of the view was modified from the
    original to use ProjectMilestone object instead of Projects - the
    action actually update project milestone objects, so this approach
    should be considerably faster.

    """

    # if is_manager(request.user) is False:
    #     return HttpResponseRedirect(reverse("ApprovedProjectsList"))

    project_formset = formset_factory(form=ApproveProjectsForm2, extra=0)

    # TODO - test that signed off and unactive projects are not included.
    # TODO - test that projects in the future are included in this year

    year = datetime.datetime.now().year

    this_year = get_approve_project_dict(year, this_year=True)
    last_year = get_approve_project_dict(year, this_year=False)

    project_filters = get_project_filters(this_year, last_year)

    if request.method == "POST":

        this_year_formset = project_formset(
            request.POST, request.FILES, initial=this_year, prefix="this_year"
        )

        last_year_formset = project_formset(
            request.POST, request.FILES, initial=last_year, prefix="last_year"
        )

        if this_year_formset.is_valid() and last_year_formset.is_valid():
            for form in this_year_formset:
                form.save()
            for form in last_year_formset:
                form.save()

            return HttpResponseRedirect(reverse("ApprovedProjectsList"))
        else:
            return render(
                request,
                "pjtk2/ApproveProjects2.html",
                {
                    "year": year,
                    "this_year_formset": this_year_formset,
                    "last_year_formset": last_year_formset,
                    "filters": project_filters,
                },
            )

    else:
        this_year_formset = project_formset(initial=this_year, prefix="this_year")
        last_year_formset = project_formset(initial=last_year, prefix="last_year")

    return render(
        request,
        "pjtk2/ApproveProjects2.html",
        {
            "year": year,
            "this_year_formset": this_year_formset,
            "last_year_formset": last_year_formset,
            "filters": project_filters,
        },
    )


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
    thisyears = (
        Project.this_year.all()
        .select_related("prj_ldr", "project_type")
        .prefetch_related("projectmilestones", "projectmilestones__milestone")
    )
    lastyears = (
        Project.last_year.all()
        .select_related("prj_ldr", "project_type")
        .prefetch_related("projectmilestones", "projectmilestones__milestone")
    )

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
# @group_required("manager")
def approve_project(request, slug):
    """
    A quick little view that will allow managers to approve projects
    from the project detail page.
    """

    if not is_manager(request.user):
        HttpResponseRedirect(reverse("ProjectList"))

    project = get_object_or_404(Project, slug=slug)
    project.approve()
    project.save()
    return HttpResponseRedirect(project.get_absolute_url())


@login_required
# @group_required("manager")
def unapprove_project(request, slug):
    """
    A quick little view that will allow managers to unapprove projects
    from the project detail page.
    """

    if not is_manager(request.user):
        HttpResponseRedirect(reverse("ProjectList"))

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

    user = User.objects.get(pk=request.user.id)
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

    user = User.objects.get(pk=request.user.id)
    project = get_object_or_404(Project, slug=slug)
    if is_manager(user):
        project.reopen()
    return HttpResponseRedirect(project.get_absolute_url())


@login_required
# @group_required("manager")
def report_milestones(request, slug):
    """
    This function will render a form of requested reporting
    requirements for each project.  Used by managers to update
    reporting requirements for each project.
    """

    if not is_manager(request.user):
        return HttpResponseRedirect(reverse("ProjectList"))

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

    user = User.objects.get(pk=request.user.id)

    milestones = (
        Milestone.objects.filter(category="Core")
        .exclude(label__in=["Approved", "Submitted", "Cancelled", "Sign off"])
        .order_by("order")
        .all()
    )

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
    employees = [x.user.id for x in employees]

    boss = False
    if len(employees) > 1:
        boss = True

    # get the submitted, approved and completed projects from the last five years
    this_year = datetime.datetime.now(pytz.utc).year

    submitted_projects = (
        Project.objects.submitted()
        .filter(owner__pk__in=employees)
        .filter(year__gte=this_year - 5)
        .values_list("pk")
    )

    prj_milestones = get_proj_ms(submitted_projects, milestones)
    submitted = make_proj_ms_dict(prj_milestones, milestones)

    approved_projects = (
        Project.objects.approved()
        .filter(owner__pk__in=employees)
        .filter(year__gte=this_year - 5)
        .values_list("pk")
    )
    prj_milestones = get_proj_ms(approved_projects, milestones)
    approved = make_proj_ms_dict(prj_milestones, milestones)

    cancelled_projects = (
        Project.objects.cancelled()
        .filter(owner__pk__in=employees)
        .filter(year__gte=this_year - 5)
        .values_list("pk")
    )

    prj_milestones = get_proj_ms(cancelled_projects, milestones)
    cancelled = make_proj_ms_dict(prj_milestones, milestones)

    completed_projects = (
        Project.objects.completed()
        .filter(owner__pk__in=employees)
        .filter(year__gte=this_year - 15)
        .values_list("pk")
    )

    prj_milestones = get_proj_ms(completed_projects, milestones)
    complete = make_proj_ms_dict(prj_milestones, milestones)

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
            "complete_count": len(completed_projects),
            "approved": approved,
            "approved_count": len(approved_projects),
            "cancelled": cancelled,
            "cancelled_count": len(cancelled_projects),
            "submitted": submitted,
            "submitted_count": len(submitted_projects),
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
    user = User.objects.get(pk=request.user.id)

    # if I am not a manager or in the list of supervisors associated
    # with this employee, return me to my projects page
    if is_manager(user) is False:
        redirect_url = reverse("MyProjects")
        return HttpResponseRedirect(redirect_url)

    # if I am the employees supervisor - get their projects and
    # associated milestones:

    milestones = (
        Milestone.objects.filter(category="Core")
        .exclude(label__in=["Approved", "Submitted", "Cancelled", "Sign off"])
        .order_by("order")
        .all()
    )

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

    submitted_projects = (
        Project.objects.submitted()
        .filter(owner=my_employee)
        .filter(year__gte=this_year - 5)
        .values_list("pk")
    )

    prj_milestones = get_proj_ms(submitted_projects, milestones)
    submitted = make_proj_ms_dict(prj_milestones, milestones)

    approved_projects = (
        Project.objects.approved()
        .filter(owner=my_employee)
        .filter(year__gte=this_year - 5)
        .values_list("pk")
    )
    prj_milestones = get_proj_ms(approved_projects, milestones)
    approved = make_proj_ms_dict(prj_milestones, milestones)

    cancelled_projects = (
        Project.objects.cancelled()
        .filter(owner=my_employee)
        .filter(year__gte=this_year - 5)
        .values_list("pk")
    )

    prj_milestones = get_proj_ms(cancelled_projects, milestones)
    cancelled = make_proj_ms_dict(prj_milestones, milestones)

    completed_projects = (
        Project.objects.completed()
        .filter(owner=my_employee)
        .filter(year__gte=this_year - 15)
        .values_list("pk")
    )

    prj_milestones = get_proj_ms(completed_projects, milestones)
    complete = make_proj_ms_dict(prj_milestones, milestones)

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
            "complete_count": len(completed_projects),
            "approved_count": len(approved_projects),
            "cancelled_count": len(cancelled_projects),
            "submitted_count": len(submitted_projects),
            "milestones": milestone_dict,
            "edit": True,
        },
    )


def sisterprojects(request, slug):
    """
    Render a form that can be used to create groupings of sister
    projects.  Only approved projects in the same year, same lake, and of the
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
