from django.forms import ModelForm
from django import forms
from pjtk2.models import Milestone, Project, ProjectReports, Reports



def make_custom_datefield(f, **kwargs):
    '''from: http://strattonbrazil.blogspot.ca/2011/03/using-jquery-uis-date-picker-on-all.html'''
    from django.db import models
    formfield = f.formfield(**kwargs)
    if isinstance(f, models.DateField):
        formfield.widget.format = '%m/%d/%Y'
        formfield.widget.attrs.update({'class':'datepicker'})
    return formfield



class CoreReportsForm(forms.Form):
    slug="LHA_IA11_998"
    corereports = Milestone.objects.filter(category='Common')
    #we need to convert the querset to a tuple of tuples
    corereports = tuple([(x[0], x[1]) for x in corereports.values_list()])
    
    if(slug):
        try:
            #get a queryset that contains the core reports that are currently
            #assigned to this project
            assigned_reports = ProjectReports.objects.filter(project__slug=
                            slug).filter(report_type__category='Common')
            initial = [x.report_type_id for x in list(assigned_reports)]
        except ProjectReports.DoesNotExist:
            initial = [x[0] for x in corereports]
    else:        
        initial = [x[0] for x in corereports]

    ckboxes = forms.MultipleChoiceField(
        choices = corereports,
        initial = initial,
        #value = False,
        label = "",
        required = True,
        widget = forms.widgets.CheckboxSelectMultiple(),
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


class DocumentForm(forms.ModelForm):
    '''A simple little demo form for testing file uploads'''
    class Meta:
        model = Reports

        
##   class DocumentForm(forms.Form):
##       reportfile = forms.FileField(
##           label='Select a file',
##           help_text='max. 42 megabytes'
##       )
##       #current = forms.BooleanField()
    #projectreport = forms.??
    #upload_date = forms.DateField(default = datetime.datetime.today)
    #uploaded_by = forms.CharField(default = "me")
    #hash = forms.CharField(default = "fakehash")    
    
