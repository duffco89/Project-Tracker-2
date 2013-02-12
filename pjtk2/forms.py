from django.forms import ModelForm
from django import forms
from pjtk2.models import Milestone, Project



def make_custom_datefield(f, **kwargs):
    '''from: http://strattonbrazil.blogspot.ca/2011/03/using-jquery-uis-date-picker-on-all.html'''
    from django.db import models
    formfield = f.formfield(**kwargs)
    if isinstance(f, models.DateField):
        formfield.widget.format = '%m/%d/%Y'
        formfield.widget.attrs.update({'class':'datepicker'})
    return formfield



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


class NewProjectForm(forms.ModelForm):
    formfield_callback = make_custom_datefield
    class Meta:
        model = Project 
