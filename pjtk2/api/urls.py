from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (ProjectViewSet, ProjectDetail,
                    ProjectPointViewSet)

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

router.register(r'projects', ProjectViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [

    url(r'^project/(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$',
        ProjectDetail.as_view()),
    url(r'^project_points/(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$',
        ProjectPointViewSet.as_view({'get':'list'}),
        name='project_points'),
    url(r'^', include(router.urls)),

    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),


]


#urlpatterns = format_suffix_patterns(urlpatterns)
