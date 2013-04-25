from django.db import models
import django_filters
from pjtk2.models import Project, TL_ProjType


class ProjectFilter(django_filters.FilterSet):
    """A filter for project lists"""
    #ProjectType = django_filters.ModelChoiceFilter(
    #              widget=django_filters.widgets.LinkWidget)  

    class Meta:
        model = Project
        fields = ['YEAR', 'ProjectType', 'Lake', 'Funding']
    
    def __init__(self, *args, **kwargs):
        #from https://github.com/alex/django-filter/issues/29
        super(ProjectFilter, self).__init__(*args, **kwargs)
        filter_ = self.filters['ProjectType']

        #self.filters['Lake'].extra.update(
        #    {'empty_label': 'All Lakes'})
        #
        #self.filters['Lake'].extra.update(
        #    {'empty_label': 'All Sources'})


        # this will grab all the fk ids that are in use
        fk_counts = Project.objects.values_list('ProjectType').order_by(
            'ProjectType').annotate(models.Count('ProjectType'))
        ProjectType_ids = [fk for fk,cnt in fk_counts]
        filter_.extra['queryset'] = TL_ProjType.objects.filter(
            pk__in=ProjectType_ids)

