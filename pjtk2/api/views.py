from rest_framework import  viewsets, status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from django.http import Http404

from .serializers import (ProjectSerializer,
                          ProjectPointSerializer)
from pjtk2.models import Project, SamplePoint



from rest_framework.pagination import PageNumberPagination

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
    Retrieveproject instance.
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
