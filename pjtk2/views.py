# E1101 - Class 'whatever' has no 'something' member
# E1120 - No value passed for parameter 'cls' in function call
# pylint: disable=E1101, E1120

import datetime
import pytz
import mimetypes
import os

from wsgiref.util import FileWrapper
from functools import partial, wraps

# from collections import OrderedDict
import collections

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.gis.geos import Polygon
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# from django.core.urlresolvers import reverse, resolve, Resolver404
from django.urls import reverse, resolve, Resolver404
from django.db.models import Q, Count, F
from django.forms.models import modelformset_factory
from django.forms import formset_factory
from django.forms import inlineformset_factory
from django.http import (
    Http404,
    HttpResponseRedirect,
    HttpResponse,
    StreamingHttpResponse,
)
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.views.generic.base import TemplateView


from taggit.models import Tag

from .functions import get_minions, my_messages, get_messages_dict, make_possessive

from .filters import ProjectFilter

from common.models import Lake

from .models import (
    Milestone,
    ProjectType,
    Project,
    Report,
    ProjectMilestones,
    Bookmark,
    Employee,
    AssociatedFile,
    ProjectFunding,
    ProjectImage,
    SamplePoint,
)  # , my_messages)

from .forms import (
    ProjectForm,
    ApproveProjectsForm,
    ReportsForm,
    SisterProjectsForm,
    # make_report_upload_form,
    ReportUploadForm,
    # ReportUploadFormSet,
    ProjectFundingForm,
    ProjectImageForm,
    EditImageForm,
    NoticesForm,
    AssociatedFileUploadForm,
    GeoForm,
)

from .spatial_utils import find_roi_projects  # ,  get_map


def get_or_none(model, **kwargs):
    """
    from http://stackoverflow.com/questions/1512059/
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def group_required(*group_names):
    """
    Requires user membership in at least one of the groups passed in.
    """
    # from:http://djangosnippets.org/snippets/1703/
    def in_groups(user):
        """
        returns true if user is in one of the groups in group_names or is a
        superuser
        """
        if user.is_authenticated:
            if bool(user.groups.filter(name__in=group_names)) | user.is_superuser:
                return True
        return False

    return user_passes_test(in_groups)


def is_manager(user):
    """
    A simple little function to find out if the current user is a
    manager (or better)
    """
    manager = False
    if user:
        if user.groups.filter(name="manager").count() > 0 | user.is_superuser:
            manager = True
        # else:
        #    manager = False
    return manager


def can_edit(user, project):
    """
    Another helper function to see if this user should be allowed
    to edit this project.  In order to edit the use must be either the
    project owner, a manager or a superuser.
    """

    if project.is_complete():
        return False

    if user:
        canedit = (
            (user.groups.filter(name="manager").count() > 0)
            or (user.is_superuser)
            or (user == project.owner)
            or (user == project.field_ldr)
        )
    else:
        canedit = False

    if canedit:
        return True
    else:
        return False


def get_assignments_with_paths(slug, core=True):
    """
    function that will return a list of dictionaries for each of the
    reporting requirements.  each dictionary will indicate what the
    report is, whether or not it has been requested for this
    project, and if it is available, a path to the associated
    report.
    """

    project = Project.objects.get(slug=slug)

    if core:
        assignments = project.get_core_assignments()
    else:
        assignments = project.get_custom_assignments()

    assign_dicts = []
    for assignment in assignments:
        try:
            report = Report.objects.get(projectreport=assignment, current=True)
        except Report.DoesNotExist:
            report = None
        required = assignment.required
        milestone = assignment.milestone
        category = assignment.milestone.category
        assign_dicts.append(
            dict(
                required=required, category=category, milestone=milestone, report=report
            )
        )
    return assign_dicts


# ===========================
# Generic Views


class HomePageView(TemplateView):
    """
    The page that will render first.
    """

    template_name = "index.html"


class ListFilteredMixin(object):
    """ Mixin that adds support for django-filter
    from: https://github.com/rasca/django-enhanced-cbv/blob/master/
                          enhanced_cbv/views/list.py
    """

    filter_set = None

    def get_filter_set(self):
        if self.filter_set:
            return self.filter_set
        else:
            raise ImproperlyConfigured(
                "ListFilterMixin requires either a definition of "
                "'filter_set' or an implementation of 'get_filter()'"
            )

    def get_filter_set_kwargs(self):
        """
        Returns the keyword arguments for instantiating the filterset.
        """

        return {"data": self.request.GET, "queryset": self.get_base_queryset()}

    def get_base_queryset(self):
        """
        We can decided to either alter the queryset before or after
        applying the FilterSet
        """

        # ==========
        self.tag = self.kwargs.get("tag", None)
        self.username = self.kwargs.get("username", None)

        if self.tag:
            queryset = Project.objects.filter(tags__name__in=[self.tag])
        elif self.username:
            # get the projects that involve this user:
            queryset = Project.objects.filter(
                Q(prj_ldr__username=self.username)
                | Q(field_ldr__username=self.username)
            )
        else:
            queryset = Project.objects.all()

        return queryset

        # ==========
        # return super(ListFilteredMixin, self).get_queryset()

    def get_constructed_filter(self):
        # We need to store the instantiated FilterSet because we use it in
        # get_queryset and in get_context_data
        if getattr(self, "constructed_filter", None):
            return self.constructed_filter
        else:
            filter = self.get_filter_set()(**self.get_filter_set_kwargs())
            self.constructed_filter = filter
            return filter

    def get_queryset(self):
        qs = self.get_constructed_filter().qs
        return qs

    def get_context_data(self, **kwargs):
        kwargs.update({"filter": self.get_constructed_filter()})
        return super(ListFilteredMixin, self).get_context_data(**kwargs)


# from django_filters.views import FilterView
# from django_filters.views import FilterMixin as _FilterMixin
#
# class FilterMixin(_FilterMixin):
#
#    def get_filterset_kwargs(self, filterset_class):
#        kwargs = super(FilterMixin, self).get_filterset_kwargs(filterset_class)
#        if kwargs['data'] is not None and 'page' in kwargs['data']:
#            data = kwargs['data'].copy() ; del data['page']
#            kwargs['data'] = data
#        return kwargs


class ProjectSearch(ListView):
    """
    """

    # modified to accept tag argument
    #
    filter_set = ProjectFilter
    # filterset_class = ProjectFilter
    template_name = "pjtk2/ProjectSearch.html"
    paginate_by = 50

    def get_queryset(self):

        search = self.request.GET.get("search")

        qs = Project.objects.select_related("project_type", "prj_ldr").all()

        if search:
            qs = qs.filter(content_search=search)

        filtered_qs = ProjectFilter(self.request.GET, qs)

        return filtered_qs.qs

    def get_context_data(self, **kwargs):
        """
        get any additional context information that has been passed in with
        the request.
        """

        context = super(ProjectSearch, self).get_context_data(**kwargs)

        context["filters"] = self.request.GET
        context["search"] = self.request.GET.get("search")
        context["first_year"] = self.request.GET.get("first_year")
        context["last_year"] = self.request.GET.get("last_year")

        lake_abbrev = self.request.GET.get("lake")
        if lake_abbrev:
            context["lake"] = Lake.objects.filter(abbrev=lake_abbrev).first()

        # need to add our factetted counts:
        qs = self.get_queryset()
        # calculate our facets by lake:
        lakes = (
            qs.select_related("lake")
            .all()
            .values(lakeName=F("lake__lake_name"), lakeAbbrev=F("lake__abbrev"))
            .order_by("lake")
            .annotate(N=Count("lake__lake_name"))
        )
        context["lakes"] = lakes

        project_types = (
            qs.select_related("project_type")
            .all()
            .values(
                projType=F("project_type__project_type"),
                projTypeId=F("project_type__id"),
            )
            .order_by("project_type")
            .annotate(N=Count("project_type"))
        )
        context["project_types"] = project_types

        project_scope = (
            qs.select_related("project_type")
            .all()
            .values(projScope=F("project_type__scope"))
            .order_by("project_type__scope")
            .annotate(N=Count("project_type__scope"))
        )

        scope_lookup = dict(ProjectType.PROJECT_SCOPE_CHOICES)
        for scope in project_scope:
            scope["name"] = scope_lookup.get(scope["projScope"])

        context["project_scope"] = project_scope

        protocols = (
            qs.select_related("protocol")
            .all()
            .values(
                projProtocol=F("protocol__protocol"),
                protocolAbbrev=F("protocol__abbrev"),
            )
            .order_by("protocol")
            .annotate(N=Count("protocol"))
        )
        context["protocols"] = protocols

        paginator = Paginator(self.object_list, self.paginate_by)
        page = self.request.GET.get("page")
        try:
            paged_qs = paginator.page(page)
        except PageNotAnInteger:
            paged_qs = paginator.page(1)
        except EmptyPage:
            paged_qs = paginator.page(paginator.num_pages)

        context["project_count"] = qs.count()
        context["object_list"] = paged_qs.object_list

        return context


class ProjectList(ListFilteredMixin, ListView):
    # class ProjectList(FilterMixin, FilterView):
    """
    A list view that can be filtered by django-filter
    """
    # modified to accept tag argument
    queryset = Project.objects.select_related("project_type", "prj_ldr").all()
    filter_set = ProjectFilter
    # filterset_class = ProjectFilter
    template_name = "pjtk2/ProjectList.html"
    paginate_by = 50

    def get_context_data(self, **kwargs):
        """
        get any additional context information that has been passed in with
        the request.
        """

        if self.username:
            try:
                prj_ldr = User.objects.get(username=self.username)
            except User.DoesNotExist:
                prj_ldr = dict(first_name=self.username, last_name="")
                # prj_ldr = None
        else:
            prj_ldr = None

        # import pdb; pdb.set_trace()

        # import pdb;pdb.set_trace()
        paginator = Paginator(self.object_list, self.paginate_by)
        page = self.request.GET.get("page")
        try:
            paged_qs = paginator.page(page)
        except PageNotAnInteger:
            paged_qs = paginator.page(1)
        except EmptyPage:
            paged_qs = paginator.page(paginator.num_pages)

        context = super(ProjectList, self).get_context_data(**kwargs)
        context["tag"] = self.tag
        context["prj_ldr"] = prj_ldr
        context["project_count"] = len(self.object_list)
        context["object_list"] = paged_qs.object_list

        return context


project_list = ProjectList.as_view()

# subset of projects tagged with tag:
taggedprojects = ProjectList.as_view()

# subset of the projects associated with a user:
user_project_list = ProjectList.as_view()


class ApprovedProjectsList(ListFilteredMixin, ListView):
    """
    A CBV that will render a list of currently approved project.
    """

    queryset = Project.objects.approved()
    filter_set = ProjectFilter
    template_name = "pjtk2/ProjectList.html"

    def get_context_data(self, **kwargs):
        context = super(ApprovedProjectsList, self).get_context_data(**kwargs)
        context["manager"] = is_manager(self.request.user)
        context["approved"] = True
        return context

    def get_base_queryset(self):
        """Start with just approved projects"""
        return Project.objects.approved()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ApprovedProjectsList, self).dispatch(*args, **kwargs)


approved_projects_list = ApprovedProjectsList.as_view()


# ===========================
# My application Views

# @login_required
def project_detail(request, slug):
    """
    View project details.
    """

    project = get_object_or_404(Project, slug=slug)

    milestones = project.get_milestones()
    core = get_assignments_with_paths(slug)
    custom = get_assignments_with_paths(slug, core=False)

    # user = User.objects.get(username__exact=request.user)
    user = get_or_none(User, username__exact=request.user)
    edit = can_edit(user, project)
    manager = is_manager(user)

    if project.cancelled:
        edit = False

    has_sister = project.has_sister()

    return render(
        request,
        "pjtk2/projectdetail.html",
        {
            "milestones": milestones,
            "Core": core,
            "Custom": custom,
            "project": project,
            "edit": edit,
            "manager": manager,
            "has_sister": has_sister,
        },
    )


def update_milestones(form_ms, milestones):
    """
    a helper function to update milestones assocaited with a project.
    events that are in form_ms but have not been completed for this
    project will be updated with a time stamp, events associated with
    this project that are not in form_ms will have their time stamp
    cleared.

    + milestones - queryset of milestones associated with a project
        generated by proj.get_milestones()

    + forms_ms - list of projectmilestone id numbers generated from
        form.cleaned_data['milestones']

    """

    # convert the list of milestones from the form to a set of integers:
    form_ms = set([int(x) for x in form_ms])

    old_completed = milestones.filter(completed__isnull=False)
    old_outstanding = milestones.filter(completed__isnull=True)

    old_completed = set([x.id for x in old_completed])
    old_outstanding = set([x.id for x in old_outstanding])

    now = datetime.datetime.now(pytz.utc)

    # these ones are now complete:
    added_ms = old_outstanding.intersection(form_ms)
    # ProjectMilestones.objects.filter(id__in=added_ms).update(completed=now)

    # in order to trigger a signal - we need to loop over each project
    # milestone, and mannually save them:
    for prjms_id in added_ms:
        prjms = ProjectMilestones.objects.get(id=prjms_id)
        prjms.completed = now
        prjms.save()

    # these ones were done, but now they aren't
    removed_ms = old_completed.difference(form_ms)
    # ProjectMilestones.objects.filter(id__in=removed_ms).update(completed=None)
    for prjms_id in removed_ms:
        prjms = ProjectMilestones.objects.get(id=prjms_id)
        prjms.completed = None
        prjms.save()


def edit_project(request, slug):
    """
    if we are editing an existing project, first make sure that this
    user has priviledges to edit this project and if so, call
    crud_project with the slug of the project and with action set to
    Edit.  If not, redirectt them back to the details page for this
    slug.
    """

    project = get_object_or_404(Project, slug=slug)

    if can_edit(request.user, project) is False:
        return HttpResponseRedirect(project.get_absolute_url())

    return crud_project(request, slug, action="Edit")


def copy_project(request, slug):
    """
    if we are copying an existing project call crud_project with the
    slug of the original project and with action set to Copy
    """
    return crud_project(request, slug, action="Copy")


def new_project(request):
    """
    if this is a new project, call crud_project without a slug and
    with action set to New
    """

    return crud_project(request, slug=None, action="New")


@login_required
def crud_project(request, slug, action="New"):
    """
    A view to create, copy and edit projects, depending on the
    value of 'action'.
    """

    if slug:
        instance = Project.objects.get(slug=slug)
        milestones = instance.get_milestones()
    else:
        instance = Project()
        milestones = None

    # find out if the user is a manager or superuser, if so set manager
    # to true so that he or she can edit all fields.
    user = User.objects.get(username__exact=request.user)
    manager = is_manager(user)

    if action == "Copy":
        milestones = None

    if action == "Edit":
        readonly = True
    else:
        readonly = False

    ProjectFundingFormset = inlineformset_factory(
        Project, ProjectFunding, form=ProjectFundingForm, extra=2
    )

    if request.method == "POST":
        if action == "Copy":
            instance = None
        form = ProjectForm(
            request.POST,
            instance=instance,
            milestones=milestones,
            readonly=readonly,
            manager=manager,
        )

        funding_formset = ProjectFundingFormset(
            request.POST, request.FILES, instance=instance
        )

        if form.is_valid():
            tags = form.cleaned_data["tags"]
            form_ms = form.cleaned_data.get("milestones", None)
            form = form.save(commit=False)
            if action == "Copy" or action == "New":
                form.owner = request.user
            funding_formset = ProjectFundingFormset(request.POST, instance=form)
            if funding_formset.is_valid():
                form.save()
                funding_formset.save()
                form.tags.set(*tags)
                if form_ms:
                    update_milestones(form_ms=form_ms, milestones=milestones)
                proj = Project.objects.get(slug=form.slug)
                return HttpResponseRedirect(proj.get_absolute_url())
        else:
            return render(
                request,
                "pjtk2/ProjectForm.html",
                {
                    "form": form,
                    "funding_formset": funding_formset,
                    "action": action,
                    "project": instance,
                },
            )
    else:
        form = ProjectForm(
            instance=instance, readonly=readonly, manager=manager, milestones=milestones
        )

    return render(
        request,
        "pjtk2/ProjectForm.html",
        {
            "form": form,
            "funding_formset": ProjectFundingFormset(instance=instance),
            "milestones": milestones,
            "action": action,
            "project": instance,
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
def report_upload(request, slug):
    """
    This view will render a formset with filefields for each of the
    reports associated with this project.  It used a custom formset
    that has been extended to accept a user and a project - these are
    needed to insert Reports.
    """

    project = Project.objects.get(slug=slug)
    has_sister = project.has_sister()

    # get the core and custom reports associated with this project
    reports = get_assignments_with_paths(slug)
    custom = get_assignments_with_paths(slug, core=False)
    if custom:
        for report in custom:
            reports.append(report)

    report_formset = formset_factory(
        wraps(ReportUploadForm)(
            partial(ReportUploadForm, project=project, user=request.user)
        ),
        extra=0,
    )

    if request.method == "POST":
        formset = report_formset(request.POST, request.FILES, initial=reports)
        if formset.is_valid():
            for form in formset:
                form.save()
            return HttpResponseRedirect(project.get_absolute_url())
    else:
        formset = report_formset(initial=reports)

    return render(
        request,
        "pjtk2/UploadReports.html",
        {"formset": formset, "project": project, "has_sister": has_sister},
    )


@login_required
def delete_report(request, slug, pk):
    """
    This view removes a report from the project detail page.  For the
    user, it will appear as though the report has been deleted.  In
    reality, the report is simply updated so that it is not longer
    rendered and available on the project detail page but it will
    still exist on the file system.

    If this is a get request, redirect to a confirmation page.  If it
    is a post, update the projectmilestone and redirect back to the
    project detail page.

    Arguments:
    - `request`:
    - `slug`:
    - `pk`:

    """
    report = get_object_or_404(Report, id=pk)
    project = get_object_or_404(Project, slug=slug)

    if not can_edit(request.user, project):
        return HttpResponseRedirect(project.get_absolute_url())

    if request.method == "POST":
        report.delete()
        return HttpResponseRedirect(project.get_absolute_url())
    else:
        return render(
            request,
            "pjtk2/confirm_report_delete.html",
            {"report": report, "project": project},
        )


@login_required
def associated_file_upload(request, slug):
    """
    This view will render a formset with filefields that can be used to
    upload files that will be associated with a specific project.
    """

    project = Project.objects.get(slug=slug)

    if request.method == "POST":
        form = AssociatedFileUploadForm(
            request.POST, request.FILES, project=project, user=request.user
        )
        if form.is_valid():
            form.save()
            # m = ExampleModel.objects.get(pk=course_id)
            # m.model_pic = form.cleaned_data['image']
            # m.save()
            return HttpResponseRedirect(project.get_absolute_url())

    else:
        return render(request, "pjtk2/UploadAssociatedFiles.html", {"project": project})


@login_required
def delete_associated_file(request, id):
    """
    This view deletes an associated file

    If this is a get request, redirect to a confirmation page.  If it
    is a post, delete the associated file o
    project detail page.

    Arguments:
    - `request`:
    - `slug`:
    - `pk`:

    """
    associated_file = get_object_or_404(AssociatedFile, id=id)
    project = associated_file.project

    if not can_edit(request.user, project):
        return HttpResponseRedirect(project.get_absolute_url())

    if request.method == "POST":
        associated_file.delete()
        return HttpResponseRedirect(project.get_absolute_url())
    else:
        return render(
            request,
            "pjtk2/confirm_file_delete.html",
            {"associated_file": associated_file, "project": project},
        )


# =================================================
#             IMAGE UPLOADING AND SORTING


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


def get_sisters_dict(slug):
    """
    given a slug, return a list of dictionaries of projects that
    are (or could be) sisters to the given project.  Values returned
    by this function are used to populate the sister project formset
    """

    project = get_object_or_404(Project, slug=slug)
    initial = []

    # family = project.get_family()
    sisters = project.get_sisters()
    candidates = project.get_sister_candidates()

    if sisters:
        for proj in sisters:
            initial.append(
                dict(
                    sister=True,
                    prj_cd=proj.prj_cd,
                    slug=proj.slug,
                    prj_nm=proj.prj_nm,
                    prj_ldr=proj.prj_ldr,
                    url=proj.get_absolute_url(),
                )
            )
    if candidates:
        for proj in candidates:
            initial.append(
                dict(
                    sister=False,
                    prj_cd=proj.prj_cd,
                    slug=proj.slug,
                    prj_nm=proj.prj_nm,
                    prj_ldr=proj.prj_ldr,
                    url=proj.get_absolute_url(),
                )
            )
    return initial


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


class ProjectTagList(ListView):
    """
    A list of tags associated with one or more projects.

    **Context:**

    ``object_list``
        a list of :model:`taggit.Tag` objects where that have been
        associated with one or more projects.

    **Template:**

    :template:`/pjtk2/project_tag_list.html`

    """

    queryset = Tag.objects.order_by("name")
    template_name = "pjtk2/project_tag_list.html"


project_tag_list = ProjectTagList.as_view()


def find_projects_roi_view(request):
    """
    Render a map in a form and return a two lists of projects - 1 is
    list of projects that are completely contained in the polygon, one
    that overlaps the polygon.
    """

    if request.method == "POST":
        form = GeoForm(request.POST)
        if form.is_valid():
            roi = form.cleaned_data["selection"][0]
            if roi.geom_type == "LinearRing":
                roi = Polygon(roi)

            project_types = form.cleaned_data["project_types"]
            first_year = form.cleaned_data["first_year"]
            last_year = form.cleaned_data["last_year"]

            projects = find_roi_projects(roi, project_types, first_year, last_year)

            # there must be a better way to do this - build the url
            # filters to be used by the api calls when the template is
            # rendered.  THe points are retrieved using ajax calls to
            # improve performance - the page loads, and then points are
            # added.
            api_filter_string = "?first_year={}&last_year={}".format(
                first_year, last_year
            )
            if project_types:
                ids = ",".join([str(x.id) for x in project_types])
                api_filter_string += "&project_type=" + ids

            return render(
                request,
                "pjtk2/show_projects_gis.html",
                {
                    "api_filter_string": api_filter_string,
                    "roi": roi,
                    "contained": projects["contained"],
                    "overlapping": projects["overlapping"],
                },
            )
        else:
            return render(
                request,
                "pjtk2/find_projects_gis.html",
                {
                    "form": form,
                    "contained": projects["contained"],
                    "overlapping": projects["overlapping"],
                },
            )
    else:
        form = GeoForm()
    return render(request, "pjtk2/find_projects_gis.html", {"form": form})


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
