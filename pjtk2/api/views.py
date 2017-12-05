from rest_framework import  viewsets, status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.http import Http404
from django.contrib.gis.geos import GEOSGeometry

from django_filters import rest_framework as filters

from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError


from .serializers import (ProjectSerializer,
                          ProjectTypeSerializer,
                          ProjectPointSerializer,
                          ProjectPolygonSerializer,
                          UserSerializer)
from pjtk2.models import Project, ProjectType, SamplePoint, ProjectPolygon, User

from pjtk2.filters import SamplePointFilter, ProjectFilter

from pjtk2.spatial_utils import find_roi_points




class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.order_by('id').all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'username'


class ProjectTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProjectType.objects.order_by('id').all()
    serializer_class = ProjectTypeSerializer
    pagination_class = StandardResultsSetPagination


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ProjectFilter


class ProjectPointViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = ProjectPointSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug').lower()
        return SamplePoint.objects.filter(project__slug=slug)


class ProjectPolygonViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = ProjectPolygonSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug').lower()
        return ProjectPolygon.objects.filter(project__slug=slug)



@api_view(['POST'])
def points_roi(request, how='contained'):
    """A view to return all of the sampling points either contained in or
    overlapping the region of interest.  Overlapping projects will have at
    least one point in the region of interest.

    The argument 'how' determines whether we return points from
    projects that were completely contained in the region of interest
    or have some of their samples in the region of interest.

    """


    #get the region of interest from the request - raise an error if we can't
    request_roi = request.GET.get("roi")
    if request_roi is None:
        request_roi = request.POST.get("roi")
        if request_roi is None:
            raise Http404

    #convert the roi string to a geos object
    try:
        roi = GEOSGeometry(request_roi)
    except ValueError:
        errmsg = 'roi could not be converted to a valid GEOS geometry.'
        raise ValidationError(errmsg)


    #try to create a polygon from our region of interest.
    # and  Raise a TypeError if roi is not a valid Linear Ring or Polygon
    if roi.geom_type not in ('Polygon', 'MultiPolygon'):
        try:
            roi = Polygon(roi)
        except:
            errmsg = 'roi is not a valid polygon.'
            raise ValidationError(errmsg)

    if how=='points_in':
        #we just want the points in the ROI, regardless of project.
        sample_points = SamplePoint.objects.filter(geom__within=roi).\
                                order_by('-project__year', 'sam')
        sample_point_filter = SamplePointFilter(request.GET, sample_points)
        serializer = ProjectPointSerializer(sample_point_filter.qs,
                                            many=True,
                                            context={'request': request})

    else:
        #get the unique project codes for all of the points that fall in
        #the region of interest
        sample_points = SamplePoint.objects.filter(geom__within=roi).\
                                distinct('project__prj_cd', 'project__year').\
                                values_list('project__prj_cd').\
                                order_by('-project__year')

        # use django-filter to parse any url parameters and filter our
        # results accordingly.
        sample_point_filter = SamplePointFilter(request.GET, sample_points)

        #get our list of unique project codes after filtering:
        prj_cds = [x[0] for x in sample_point_filter.qs]
        points = find_roi_points(roi, prj_cds)

        #serialize the points based on the value of 'how' (either 'overlapping' or
        #'contained'):
        serializer = ProjectPointSerializer(points[how], many=True,
                                            context={'request': request})

    return Response(serializer.data)
