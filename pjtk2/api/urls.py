from django.conf import settings
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (
    UserViewSet,
    ProjectViewSet,
    ProjectTypeViewSet,
    ProjectPointViewSet,
    ProjectPolygonViewSet,
    points_roi,
)

app_name = "api"

PRJ_CD_REGEX = settings.PRJ_CD_REGEX

router = routers.DefaultRouter()

router.register(r"projects", ProjectViewSet)
router.register(r"project_leads", UserViewSet, basename="project_lead")
router.register(r"project_types", ProjectTypeViewSet, basename="project_type")

urlpatterns = [
    url(
        r"^project_points/" + PRJ_CD_REGEX,
        ProjectPointViewSet.as_view({"get": "list"}),
        name="project_points",
    ),
    url(
        r"^project_polygon/" + PRJ_CD_REGEX,
        ProjectPolygonViewSet.as_view({"get": "list"}),
        name="project_polygon",
    ),
    # just the points - regardless of project
    url(r"points_in_roi/", points_roi, {"how": "points_in"}, name="get_points_in_roi"),
    # points for projects were ALL points are in roi
    url(
        r"project_points_contained_in_roi/",
        points_roi,
        {"how": "contained"},
        name="get_project_points_contained_in_roi",
    ),
    # points for projects were SOME points are in roi
    url(
        r"project_points_overlapping_roi/",
        points_roi,
        {"how": "overlapping"},
        name="get_project_points_overlapping_roi",
    ),
    url(r"^", include(router.urls)),
    url(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]


# urlpatterns = format_suffix_patterns(urlpatterns)
