
from rest_framework import serializers

from pjtk2.models import Project, SamplePoint


class ProjectSerializer(serializers.HyperlinkedModelSerializer):

    sample_points = serializers.HyperlinkedIdentityField(
        view_name='project_points', lookup_field='slug')

    class Meta:
        model = Project
        fields = ('year', 'prj_cd', 'slug', 'prj_nm', 'prj_date0', 'prj_date1',
                  'prj_ldr', 'sample_points', 'comment_html')


class ProjectPointSerializer(serializers.HyperlinkedModelSerializer):

    prj_cd = serializers.CharField(source='project.prj_cd', read_only=True)

    class Meta:
        model = SamplePoint
        fields = ('project', 'prj_cd', 'sam', 'geom', 'dd_lat', 'dd_lon',
                  'popup_text',
                  )
