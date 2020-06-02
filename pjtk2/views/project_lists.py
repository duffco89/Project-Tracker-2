"""=============================================================
 ~/pjtk2/views/project_lists.py
 Created: 24 Apr 2020 17:56:13

 DESCRIPTION:

  The views in this file return different types of project lists - the
  default list, search list, list by tag, list by project lead,
  approved projects, ect.

 A. Cottrill
=============================================================

"""


# E1101 - Class 'whatever' has no 'something' member
# E1120 - No value passed for parameter 'cls' in function call
# pylint: disable=E1101, E1120


from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Polygon
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, F
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.shortcuts import render

from taggit.models import Tag

from common.models import Lake

from ..models import Project, ProjectType
from ..forms import GeoForm

from ..filters import ProjectFilter

from ..utils.helpers import is_manager

from ..utils.spatial_utils import find_roi_projects  # ,  get_map


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

        queryset = Project.objects.select_related("prj_ldr", "project_type")

        # ==========
        self.tag = self.kwargs.get("tag", None)
        self.username = self.kwargs.get("username", None)

        if self.tag:
            queryset = queryset.filter(tags__name__in=[self.tag])
        elif self.username:
            # get the projects that involve this user:
            queryset = queryset.filter(
                Q(prj_ldr__username=self.username)
                | Q(field_ldr__username=self.username)
            )

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
    queryset = (
        Project.objects.select_related("prj_ldr").prefetch_related("project_type").all()
    )
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


class ApprovedProjectsList(ListView):
    """
    A CBV that will render a list of currently approved project.
    """

    # queryset = Project.objects.approved()
    filter_set = ProjectFilter
    template_name = "pjtk2/ProjectList.html"
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super(ApprovedProjectsList, self).get_context_data(**kwargs)
        context["manager"] = is_manager(self.request.user)
        context["approved"] = True
        return context

    def get_queryset(self):
        """Start with just approved projects"""
        qs = (
            Project.objects.approved()
            .select_related("project_type", "prj_ldr")
            .prefetch_related("projectmilestones", "projectmilestones__milestone")
        )

        filtered_qs = ProjectFilter(self.request.GET, qs)

        return filtered_qs.qs

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ApprovedProjectsList, self).dispatch(*args, **kwargs)


approved_projects_list = ApprovedProjectsList.as_view()


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
