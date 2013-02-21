from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User

from django.utils.safestring import mark_safe

from pjtk2.models import Milestone, Project, ProjectReports, Report, TL_ProjType, TL_Database
import pdb
import re

def make_custom_datefield(f, **kwargs):
    '''from: http://strattonbrazil.blogspot.ca/2011/03/using-jquery-uis-date-picker-on-all.html'''
    from django.db import models
    formfield = f.formfield(**kwargs)
    if isinstance(f, models.DateField):
        formfield.widget.format = '%m/%d/%Y'
        formfield.widget.attrs.update({'class':'datepicker'})
    return formfield


class CoreReportsForm(forms.Form):
    #pass
    def __init__(self, *args, **kwargs):
        self.reports = kwargs.pop('reports')
        #self.reports = kwargs['reports']
        super(CoreReportsForm, self).__init__(*args, **kwargs)
        corereports = self.reports["core"]["reports"]
        assigned = self.reports["core"]["assigned"]
        
        self.fields['core'] = forms.MultipleChoiceField(
            choices = corereports,
            initial = assigned,
            label = "",
            required = True,
            widget = forms.widgets.CheckboxSelectMultiple(),
            )

        self.fields['custom'] = forms.MultipleChoiceField(
            choices = self.reports["custom"]["reports"],
            initial = self.reports["custom"]["assigned"],
            label = "",
            required = True,
            )


    
##          #slug = self.slug
##          #slug = project.slug
##          #slug="LHA_IA11_998"
##  
##          #pdb.set_trace()
##      
##      corereports = Milestone.objects.filter(category='Common')
##      #we need to convert the querset to a tuple of tuples
##      corereports = tuple([(x[0], x[1]) for x in corereports.values_list()])
##  
##      if(slug):
##          try:
##              #get a queryset that contains the core reports that are currently
##              #assigned to this project
##              assigned_reports = ProjectReports.objects.filter(project__slug=
##                              slug).filter(report_type__category='Common')
##              initial = [x.report_type_id for x in list(assigned_reports)]
##          except ProjectReports.DoesNotExist:
##              initial = [x[0] for x in corereports]
##      else:
##          initial = [x[0] for x in corereports]
##  
##  
##          #inital and choices will be passed in as elements of "extra_args"
##          
##      ckboxes = forms.MultipleChoiceField(
##          choices = corereports,
##          initial = initial,
##          label = "",
##          required = True,
##          widget = forms.widgets.CheckboxSelectMultiple(),
##          )

class AdditionalReportsForm(forms.Form):
    reports = Milestone.objects.filter(category='Custom')
    #we need to convert the querset to a tuple of tuples
    reports = tuple([(x[0], x[1]) for x in reports.values_list()])
    ckboxes = forms.MultipleChoiceField(
        choices = reports,
        label = "",
        required = True,
        )


##  class NewProjectForm(forms.ModelForm):
##      formfield_callback = make_custom_datefield
##      class Meta:
##          model = Project
##          exclude = ("slug", "YEAR", "Owner",)

CHOICE_LIST = [
    ('', '----'), # replace the value '----' with whatever you want, it won't matter
    (1, 'Rock'),
    (2, 'Hard Place')
]

class NewProjectForm(forms.Form):
    '''This a form for new projects using crispy-forms and including
    cleaning methods to ensure that project code is valid, dates agree
    and ....  for a new project, we need project code, name, comment,
    leader, start date, end date, database, project type,'''

    PROJ_TYPES = TL_ProjType.objects.all()
    MASTER_DBs = TL_Database.objects.all()    
    
    PRJ_NM = forms.CharField(
        label = "Project Name:",
        max_length = 200,
        required = True,
    )
    
    PRJ_CD = forms.CharField(
        label = "Project Code:",
        max_length = 80,
        required = True,
    )

    PRJ_LDR = forms.CharField(
        label = "Project Leader:",
        max_length = 80,
        required = True,
    )
    
    COMMENT = forms.CharField(
        widget = forms.Textarea(),
        label = "Brief Project Description:",
        required=True,
        )
    
    PRJ_DATE0 = forms.DateField(
        label = "Start Date:",
        required = True,
    )

    PRJ_DATE1 = forms.DateField(
        label = "End Date:",
        required = True,
    )
    
    ProjectType = forms.ChoiceField(
        label = "Project Type:",
        choices=  [(x.id, x.Project_Type) for x in PROJ_TYPES],
        required = True,
    )

    MasterDatabase = forms.ChoiceField(
        label = "Master Database:",
        choices = [(x.id, x.MasterDatabase) for x in MASTER_DBs],        
        required = True,
    )


    Keywords = forms.CharField(
        label = "Keywords:",
        max_length = 80,
        required = False,
    )

    
    def __init__(self, user, *args, **kwargs):
        #user = kwargs.pop('user')
        self.helper = FormHelper()
        self.helper.form_id = 'ProjectForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = ''

        self.helper.layout = Layout(
        Fieldset(
                'Project Elements',
                'PRJ_NM',                
                'PRJ_CD',
                'PRJ_LDR',                
                'COMMENT',                
                Field('PRJ_DATE0', datadatepicker='datepicker'),                
                Field('PRJ_DATE1', datadatepicker='datepicker'),
                'ProjectType',
                'MasterDatabase',                
                'Keywords',
        #Field('Owner', type='hidden'),
                HTML("""<p><em>(comma separated values)</em></p> """),
            ),
            ButtonHolder(
                Submit('submit', 'Submit')
            )
        )

        super(NewProjectForm, self).__init__(*args, **kwargs)
        #self.fields['Owner'].queryset = User.objects.filter(pk = user.id)
        self.user = user

    
    def clean_PRJ_CD(self):
        '''a clean method to ensure that the project code matches the
        following regular expression:
        NOTE: field name must match exactly!
        '''
        pattern  = "^[A-Z]{3}_[A-Z]{2}\d{2}_([A-Z]|\d){3}$"

        project_code =  self.cleaned_data["PRJ_CD"]
        if re.search(pattern, project_code):
            #make sure that this project code doesn't already exist:
            try:
                proj = Project.objects.get(PRJ_CD=project_code)
            except Project.DoesNotExist:
                proj = None
            if proj:
                url = proj.get_absolute_url()
                print url
                errmsg = "Project Code already exists (<a href='%s'>view</a>)." % url
                raise forms.ValidationError(mark_safe(errmsg))
            else:
                return project_code
        else:
            raise forms.ValidationError("Malformed Project Code.")
            

    def clean(self):
        '''make sure that project start and end dates are in the same
        year, and that the start date occurs before the end date.
        Also make sure that the year in project code matches the start
        and end dates.'''

        cleaned_data = super(NewProjectForm, self).clean()
        start_date = cleaned_data.get('PRJ_DATE0')
        end_date = cleaned_data.get('PRJ_DATE1')
        project_code = cleaned_data.get('PRJ_CD')
        
        if start_date and end_date and project_code:
                
            if end_date < start_date:
                errmsg = "Project end date occurs before start date."
                raise forms.ValidationError(errmsg)
            if end_date.year != start_date.year:
                errmsg = "Project start and end date occur in different years."
                raise forms.ValidationError(errmsg)
            
            if end_date.strftime("%y") != project_code[6:8]:
                errmsg = "Project dates do not agree with project code."
                raise forms.ValidationError(errmsg)

        return cleaned_data
        
         
    def save(self):
        '''A custom method to save the new project to the
        database. Once saved, automatically create create records in
        ProjectReports table to serve as place holders for the core
        reports.'''

        new_project = Project.objects.create(
                PRJ_CD = self.cleaned_data["PRJ_CD"],
                PRJ_NM = self.cleaned_data["PRJ_NM"],
                PRJ_LDR = self.cleaned_data["PRJ_LDR"],
                PRJ_DATE0 = self.cleaned_data["PRJ_DATE0"],                
                PRJ_DATE1 = self.cleaned_data["PRJ_DATE1"],
                COMMENT = self.cleaned_data["COMMENT"],
                ProjectType = TL_ProjType.objects.get(id=self.cleaned_data["ProjectType"]),
                MasterDatabase = TL_Database.objects.get(id=self.cleaned_data["MasterDatabase"]),
                Owner = self.user,
                )

        return new_project

        
class DocumentForm(forms.ModelForm):
    '''A simple little demo form for testing file uploads'''
    class Meta:
        model = Report


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



## ===========================================================
##   CRISPY FORM EXAMPLE


# -*- coding: utf-8 -*-
from django import forms
 
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
 
class CrispyForm(forms.Form):
    
    text_input = forms.CharField()

    textarea = forms.CharField(
        widget = forms.Textarea(),
        )

    radio_buttons = forms.ChoiceField(
        choices = (
            ('option_one', "Option one is this and that be sure to include why it's great"),
            ('option_two', "Option two can is something else and selecting it will deselect option one")),
            widget = forms.RadioSelect,
            initial = 'option_two',
    )

    checkboxes = forms.MultipleChoiceField(
        choices = (
            ('option_one', "Option one is this and that be sure to include why it's great"),
            ('option_two', 'Option two can also be checked and included in form results'),
            ('option_three', 'Option three can yes, you guessed it also be checked and included in form results')),
            initial = 'option_one',
            widget = forms.CheckboxSelectMultiple,
            help_text = "<strong>Note:</strong> Labels surround all the options for much larger click areas and a more usable form.",
    )

    appended_text = forms.CharField(
        help_text = "Here's more help text"
        )

    prepended_text = forms.CharField()

    prepended_text_two = forms.CharField()

    multicolon_select = forms.MultipleChoiceField(
    choices = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')),
    )

    # Uni-form
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('text_input', css_class='input-xlarge'),
        Field('textarea', rows="3", css_class='input-xlarge'),
        'radio_buttons',
        Field('checkboxes', style="background: #FAFAFA; padding: 10px;"),
        AppendedText('appended_text', '.00'),
        PrependedText('prepended_text', '<input type="checkbox" checked="checked" value="" id="" name="">', active=True),
        PrependedText('prepended_text_two', '@'),
        'multicolon_select',
    FormActions(
        Submit('save_changes', 'Save changes', css_class="btn-primary"),
        Submit('cancel', 'Cancel'),
    )
    )

    # from http://django-crispy-forms.readthedocs.org/en/1.2.1/tags.html
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, MultiField

    
class ExampleForm(forms.Form):
    like_website = forms.TypedChoiceField(
        label = "Do you like this website?",
        choices = ((1, "Yes"), (0, "No")),
        coerce = lambda x: bool(int(x)),
        widget = forms.RadioSelect,
        initial = '1',
        required = True,
    )

    favorite_food = forms.CharField(
        label = "What is your favorite food?",
        max_length = 80,
        required = True,
    )

    favorite_color = forms.CharField(
        label = "What is your favorite color?",
        max_length = 80,
        required = True,
    )

    favorite_number = forms.IntegerField(
        label = "Favorite number",
        required = False,
    )

    birth_date = forms.DateField(
        label = "BirthDate",
        required = False,
    )

    
    notes = forms.CharField(
        label = "Additional notes or feedback",
        required = False,
    )    



    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'
        #self.helper.add_input(Submit('submit', 'Submit'))

        self.helper.layout = Layout(

##          MultiField(
##              'Tell us your favorite stuff {{ username }}',
##              Div(
##                  'like_website',
##                  'favorite_number',
##                  css_id = 'special-fields'
##              ),
##              'favorite_color',
##              'favorite_food',
##              'notes'
##              )
##           
            Fieldset(
                'first arg is the legend of the fieldset',
                'like_website',
                'favorite_number',
                'favorite_color',
                'favorite_food',
                Field('birth_date', datadatepicker='datepicker'),
                HTML("""<p>We use notes to get better, <strong>please help us {{ username }}</strong></p> """),                
                'notes'
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )

        
        super(ExampleForm, self).__init__(*args, **kwargs)
