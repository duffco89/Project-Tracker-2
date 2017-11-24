from rest_framework import  viewsets, status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.http import Http404
from django.contrib.gis.geos import GEOSGeometry

from .serializers import (ProjectSerializer,
                          ProjectPointSerializer,
                          ProjectPolygonSerializer)
from pjtk2.models import Project, SamplePoint, ProjectPolygon

from pjtk2.filters import SamplePointFilter

from pjtk2.spatial_utils import find_roi_points

from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = StandardResultsSetPagination


class ProjectDetail(RetrieveAPIView):
    """
    Retrieve project instance.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


    def get_object(self):
        try:
            slug = self.kwargs.get('slug').lower()
            return Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            raise Http404


class ProjectPointViewSet(viewsets.ModelViewSet):

    serializer_class = ProjectPointSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug').lower()
        return SamplePoint.objects.filter(project__slug=slug)


class ProjectPolygonViewSet(viewsets.ModelViewSet):

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

    request_roi = request.GET.get("roi")
    #roi = request.POST.get("roi")
    if request_roi is None:
        request_roi = request.POST.get("roi")
        if request_roi is None:
            raise Http404

    try:
        roi = GEOSGeometry(request_roi)
    except ValueError:
        errmsg = ['roi could not be converted to a valid GEOS geometry.']
        raise ValidationError(errmsg)

    #try to create a polygon from our region of interest.
    # and  Raise a TypeError if roi is not a valid Linear Ring or Polygon
    if roi.geom_type!='Polygon':
        try:
            roi = Polygon(roi)
        except:
            errmsg = ['roi is not a valid polygon.']
            raise ValidationError(errmsg)


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
