from django import forms
from django.db import models
import django_filters

from pjtk2.models import Project, ProjectType, Lake

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,  Field, Submit


def get_year_choices():
    """a little helper function to get a distinct list of years that can
    be used for the years filter.  The function returns a list of two
    element tuples.  the first tuple is an empty string and its
    indicator, the remaining tuples are each of the distinct years in
    Projects, sorted in reverse chronological order.
    """
    years = Project.objects.values_list('year')
    years = list(set([x[0] for x in years]))
    years.sort(reverse=True)
    years = [(x, x) for x in years]
    years.insert(0, ('', '---------'))
    return years



class ProjectFilter(django_filters.FilterSet):
    """A filter for project lists"""

    class Meta:
        model = Project
        #fields = ['year', 'project_type', 'lake', 'funding']
        fields = ['year', 'project_type', 'lake']

    def __init__(self, *args, **kwargs):
        #from https://github.com/alex/django-filter/issues/29
        super(ProjectFilter, self).__init__(*args, **kwargs)
        filter_ = self.filters['project_type']

        #self.filters['lake'].extra.update(
        #    {'empty_label': 'All lakes'})
        #
        #self.filters['lake'].extra.update(
        #    {'empty_label': 'All Sources'})

        # this will grab all the fk ids that are in use
        fk_counts = Project.objects.values_list('project_type').order_by(
            'project_type').annotate(models.Count('project_type'))
        ProjectType_ids = [fk for fk,cnt in fk_counts]
        filter_.extra['queryset'] = ProjectType.objects.filter(
            pk__in=ProjectType_ids)

    @property
    def form(self):
        self._form = super(ProjectFilter, self).form
        self._form.helper = FormHelper()
        #self._form.helper.form_tag = False
        self._form.helper.form_style = 'inline'
        self._form.helper.form_method = 'get'
        self._form.helper.form_action = ''

        self._form.fields.update({"year": forms.ChoiceField(
            label="Year:", choices=get_year_choices(),
            required=False)})

        self._form.fields.update({"lake": forms.ModelChoiceField(
            label="Lake:", queryset=Lake.objects.all(),
            required=False)})

        #self._form.fields.update({"project_type": forms.ModelChoiceField(
        #    label="Project Type:", queryset=ProjectType.objects.all(),
        #    required=False)})

        self._form.helper.add_input(Submit('submit', 'Apply Filter'))
        self._form.helper.layout = Layout(
            Field('year'),
            Field('project_type'),
            Field('lake'),
            #Field('funding'),
        )

        return self._form
