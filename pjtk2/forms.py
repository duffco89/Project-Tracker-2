from django import forms
from pjtk2.models import Milestone

class CoreReportsForm(forms.Form):
    reports = Milestone.objects.filter(category='Common')
    #we need to convert the querset to a tuple of tuples
    reports = tuple([(x[0], x[1]) for x in reports.values_list()])
    ckboxes = forms.MultipleChoiceField(
        choices = reports,
        label = "",
        required = True,
        widget = forms.widgets.CheckboxSelectMultiple
        )

class AdditionalReportsForm(forms.Form):
    reports = Milestone.objects.filter(category='Custom')
    #we need to convert the querset to a tuple of tuples
    reports = tuple([(x[0], x[1]) for x in reports.values_list()])
    ckboxes = forms.MultipleChoiceField(
        choices = reports,
        label = "",
        required = True,
        )
    
