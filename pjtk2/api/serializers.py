from rest_framework import serializers
from django.contrib.auth import get_user_model
from pjtk2.models import Project, ProjectType, SamplePoint, ProjectPolygon

User = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        lookup_field = "username"
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
        )
        ordering = ["id"]


class ProjectTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProjectType
        fields = ("project_type", "field_component")
        ordering = ["id"]


class ProjectSerializer(serializers.HyperlinkedModelSerializer):

    sample_points = serializers.HyperlinkedIdentityField(
        view_name="api:project_points", lookup_field="slug"
    )

    prj_ldr = UserSerializer()

    project_type = serializers.CharField(
        source="project_type.project_type", read_only=True
    )

    class Meta:
        model = Project
        lookup_field = "slug"
        fields = (
            "year",
            "prj_cd",
            "slug",
            "prj_nm",
            "prj_date0",
            "prj_date1",
            "project_type",
            "prj_ldr",
            "comment",
            "sample_points",
        )


class ProjectPointSerializer(serializers.HyperlinkedModelSerializer):

    # project = serializers.HyperlinkedIdentityField(
    #    view_name='api:project-detail',
    #    lookup_field='project.slug',
    #    read_only=True)

    prj_cd = serializers.CharField(source="project.prj_cd", read_only=True)
    project_type = serializers.CharField(source="project.project_type", read_only=True)

    class Meta:
        model = SamplePoint
        fields = (  #'project',
            "prj_cd",
            "label",
            # "geom",
            "dd_lat",
            "dd_lon",
            "popup_text",
            "project_type",
        )


class ProjectPolygonSerializer(serializers.HyperlinkedModelSerializer):

    prj_cd = serializers.CharField(source="project.prj_cd", read_only=True)

    class Meta:
        model = ProjectPolygon
        fields = ("prj_cd", "geom")
