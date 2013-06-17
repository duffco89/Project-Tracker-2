from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from django import forms
from django.contrib.auth.models import User

from django.utils.safestring import mark_safe


from taggit.forms import *
from pjtk2.models import (Milestone, Project, ProjectMilestones, Report, 
                          TL_ProjType, TL_Database, TL_Lake)
from pjtk2.models import ProjectSisters
import pdb
import re
import hashlib

#from functions import *

#==================================
#  WIDGETS

def make_custom_datefield(f, **kwargs):
    '''from: http://strattonbrazil.blogspot.ca/2011/03/using-jquery-uis-date-picker-on-all.html'''
    from django.db import models
    formfield = f.formfield(**kwargs)
    if isinstance(f, models.DateField):
        formfield.widget.format = '%m/%d/%Y'
        formfield.widget.attrs.update({'class':'datepicker'})
    return formfield


class ReadOnlyText(forms.TextInput):
  '''from:
  http://stackoverflow.com/questions/1134085/rendering-a-value-as-text-instead-of-field-inside-a-django-form'''

  input_type = 'text'
  def render(self, name, value, attrs=None):
     if value is None: 
         value = ''
     return value

class HyperlinkWidget(forms.TextInput):
    """This is a widget that will insert a hyperlink to a project
    detail page in a form set.  Currently, the url is hardwired and
    should be updated using get_absolute_url"""
    
    def __init__(self, attrs={}):
        super(HyperlinkWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value is None:
            value = ''
        output.append('<a href="/test/projectdetail/%s/">%s</a>' % (value.lower(), value))
        return mark_safe(u''.join(output))

#==================================
#  FORMS

        
class ApproveProjectsForm(forms.ModelForm):
    '''This project form is used for view to approve/unapprove
    multiple projects.'''

    Approved = forms.BooleanField(
        label = "Approved:",
        required =False,
    )
    
    PRJ_NM = forms.CharField(
        widget = ReadOnlyText,
        label = "Project Name",
        required =False,
    )
    
    PRJ_CD = forms.CharField(
        widget = HyperlinkWidget,
        label = "Project Code",
        max_length = 80,
        required = False,
    )

    PRJ_LDR = forms.CharField(
        widget = ReadOnlyText,
        label = "Project Leader",
        max_length = 80,
        required = False,
    )


    
    class Meta:
        model=Project
        fields = ('Approved', 'PRJ_CD', 'PRJ_NM', 'PRJ_LDR') 

    def clean_PRJ_CD(self):
        '''return the original value of PRJ_CD'''
        return self.instance.PRJ_CD
        
    def clean_PRJ_NM(self):
        '''return the original value of PRJ_NM'''
        return self.instance.PRJ_NM

    def clean_PRJ_LDR(self):
        '''return the original value of PRJ_LDR'''
        return self.instance.PRJ_LDR
        





class ReportsForm(forms.Form):
    '''This form is used to update reporting requirements for a
    particular project.  Checkbox widgets are dynamically added to the
    form depending on reports identified as core plus any additional
    custom reports requested by the manager.'''
    
    def __init__(self, *args, **kwargs):
        self.reports = kwargs.pop('reports')
        self.core = kwargs.pop('Core', True)
        self.project = kwargs.pop('project', None)
        
        super(ReportsForm, self).__init__(*args, **kwargs)
        if self.core:
            what = 'Core'
        else:
            what = 'Custom'

        self.what = what
        
        reports = self.reports[what]["reports"]
        assigned = self.reports[what]["assigned"]
        
        self.fields[what] = forms.MultipleChoiceField(
            choices = reports,
            initial = assigned,
            label = "",
            required = False,
            widget = forms.widgets.CheckboxSelectMultiple(),
            )
        

    def save(self):
        cleaned_data = self.cleaned_data
        project = self.project
        what = self.what

        #turn OFF any ProjectMilestones that are not in cleaned data
        ProjectMilestones.objects.filter(project = project).exclude(milestone__in=
                  cleaned_data[what]).filter(milestone__category=
                  what.title()).update(required=False)

        #turn ON any ProjectMilestones that are in cleaned data
        ProjectMilestones.objects.filter(project = 
                  project).filter(milestone__category=
                  what.title()).filter(milestone__in=cleaned_data[what]).update(required=True)

        #now we need to see if there are any new reports for this project
        #queryset of all 'what' (custom or core) reports assocaited with project
        jj=ProjectMilestones.objects.filter(project=project).filter(milestone__category=what.title())
        #id numbers for milestone objects already associated with this project
        in_ProjectMilestones = str([x['milestone_id'] for x in jj.values()])

        # these are the new custom reports types id's that need to associated with
        # this project (ones in cleaned_data but not in ProjectMilestones)
        newreports = list(set(cleaned_data.values()[0])-set(in_ProjectMilestones))

        #Then loop over new reports adding a new record for each one with
        #required=True
        if newreports:
            for report in newreports:
                ProjectMilestones.objects.create(project=project,
                                              required=True, 
                                              milestone_id=report)


class ReportUploadFormSet(BaseFormSet):
    '''modified from
    here:http://stackoverflow.com/questions/5426031/django-formset-set-current-user
    allows additional parameters to be passed to formset.  Project and
    user are required to upload reports.

    This formset is used to upload the reports for a particular
    project.  It will generate one reportUploadForm for each reporting
    requirement (all core reports plus any additional reports that
    have been requested).

    Additionally, the project and user id will associated with each
    form so that they can be appended and uploaded properly.
    '''
    def __init__(self, *args, **kwargs):
        self. project = kwargs.pop('project', None)
        self. user = kwargs.pop('user', None)
        super(ReportUploadFormSet, self).__init__(*args, **kwargs)

    def _construct_forms(self): 
        self.forms = []
        for i in xrange(self.total_form_count()):
            self.forms.append(self._construct_form(i, project=self.project,
                                                   user=self.user))
        

class ReportUploadForm(forms.Form):
    """This form is used in ReportUploadFormset to upload files. Each
    form includes a label for the report type, a read only checkbox
    indicating whether or not this report is required, and a file
    input widget.""" 

    required = forms.BooleanField(
        label = "Required",
        required =False,
    )
    
    milestone = forms.CharField(
        widget = ReadOnlyText,
        label = "Report Name",
        required =False,
    )

    report_path = forms.FileField(
        label = "File",
        required =False,        
        )    

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        self.user = kwargs.pop('user')
        super(ReportUploadForm, self).__init__(*args, **kwargs)
        self.fields["required"].widget.attrs['disabled'] = True
        #self.fields["report_path"].widget.attrs['style'] = "text-align: right;"
        self.fields["report_path"].widget.attrs['size'] = "40"        
        self.fields["report_path"].widget.attrs['class'] = "fileinput"        
                         
    def clean_milestone(self):
        '''return the original value of milestone'''
        return self.initial['milestone']

    def clean_required(self):
        '''return the original value of required'''
        return self.initial['required']
                
    def save(self):
        '''see if a report already exists for this projectreport, if
        so, make sure that it Current flag is set to false 
        
        - populate uploaded by with user name
        
        - TODO:calculate hash of file (currently calculated on hash of path)
        
        - TODO:verify that it matches certain criteria (file
        types/extentions) depending on reporting milestone
        
        - if this is a presentation or summary report, see if the
        project has any sister projects, if so, update projectreports
        for them too.
        '''


        #if 'report_path' in self.changed_data:        
        if 'report_path' in self.changed_data and self.cleaned_data['report_path']:        
           
            projectreport = ProjectMilestones.objects.get(
                project=self.project, milestone=self.clean_milestone())

            #see if there is already is a report for this projectreport
            try:
                oldReport = Report.objects.get(projectreport=projectreport, 
                                               current=True)
            except Report.DoesNotExist:
                oldReport = None

            #if so set the 'current' attribure of the old report to
            #False so that it can be replaced by the new one (there
            #can only ever be one 'current' report)
            if oldReport:
                oldReport.current = False
                oldReport.save()

            self.is_valid() #just to make sure

            newReport = Report(
                    report_path = self.cleaned_data['report_path'],
                    uploaded_by = self.user.username,
                    report_hash = hashlib.sha1(
                        str(self.cleaned_data['report_path'])).hexdigest()

                )
            newReport.save()
            #add the m2m record for this projectreport
            newReport.projectreport.add(projectreport)
            
            #if this a presentation or summary report, see if
            #this project has any sister projects.  If so, add an m2m
            #for each one so this document is associated with them
            #too.  
            #TODO: figure out how to handle sisters
            #that are adopted or dis-owned - how do we synchronize
            #existing files?
            
            sisters = self.project.get_sisters()
            #TODO: change reporting milestone model to include
            #"Copy2Sisters" flag - then this list could be refactored
            #to dynamic query
            common = str(self.clean_milestone()) in ["Proposal Presentation",
                                                "Completetion Presentation",
                                                "Summary Report",] 
            
            if sisters and common:
                for sister in sisters:
                    #projectreport = ProjectMilestones.objects.get(
                    #    project=sister, 
                    #    milestone=self.clean_milestone())
                    projectreport, created = ProjectMilestones.objects.get_or_create(
                        project=sister, milestone=self.clean_milestone())
                    try:
                        oldReport = Report.objects.get(projectreport=projectreport, 
                                                       current=True)
                        oldReport.current = False
                        oldReport.save()

                    except Report.DoesNotExist:
                        oldReport = None

                    #if oldReport:
                    #    oldReport.current = False
                    #    oldReport.save()
                    #add the m2m relationship for the sister
                    newReport.projectreport.add(projectreport)



class ProjectForm(forms.ModelForm):
    '''This a form for new projects using crispy-forms and including
    cleaning methods to ensure that project code is valid, dates agree
    and ....  for a new project, we need project code, name, comment,
    leader, start date, end date, database, project type,'''
    
    PRJ_NM = forms.CharField(
        label = "Project Name:",
        required = True,
    )
    
    PRJ_CD = forms.CharField(
        label = "Project Code:",
        max_length = 12,
        required = True,
    )

    PRJ_LDR = forms.CharField(
        label = "Project Leader:",
        required = True,
    )
    
    COMMENT = forms.CharField(
        widget = forms.Textarea(),
        label = "Brief Project Description:",
        required=True,
        )

    RISK = forms.CharField(
        widget = forms.Textarea(),
        label = "Risks associated with not running project:",
        required=False,
        )

    
    PRJ_DATE0 = forms.DateField(
        label = "Start Date:",
        required = True,
    )

    PRJ_DATE1 = forms.DateField(
        label = "End Date:",
        required = True,
    )
    
    ProjectType = forms.ModelChoiceField(
        label = "Project Type:",
        queryset = TL_ProjType.objects.all(),
        required = True,
    )
    
    MasterDatabase = forms.ModelChoiceField(
        label = "Master Database:",
        queryset = TL_Database.objects.all(),
        required = True,
    )

    TL_Lake = forms.ModelChoiceField(
        label = "Lake:",
        queryset = TL_Lake.objects.all(),
        required = True,
    )

    DBA = forms.ModelChoiceField(
        label = "Data Custodian:",
        #TODO - change this from superuser to groups__contain='dba'
        queryset = User.objects.filter(is_superuser=True),
        required = True,
    )

    
    tags = TagField(
        label="Keywords:",
        required = False)

    Approved = forms.BooleanField(
        label = "Approved",
        required =False,
    )

    Conducted = forms.BooleanField(
        label = "Conducted",
        required =False,
    )

    DataScrubbed = forms.BooleanField(
        label = "DataScrubbed",
        required =False,
    )

    DataMerged = forms.BooleanField(
        label = "Data Merged",
        required =False,
    )

    SignOff = forms.BooleanField(
        label = "Sign Off",
        required =False,
    )
    
    class Meta:
        model=Project
        #exclude = ("slug", "YEAR", "Owner", "Max_DD_LAT", 
        #           "Max_DD_LON", "Min_DD_LAT", "Min_DD_LON")
        fields = ("PRJ_NM", "PRJ_LDR", "PRJ_CD", "PRJ_DATE0", "PRJ_DATE1", "RISK",
                   "Approved", "Conducted", "DataScrubbed", "DataMerged", "SignOff",
                    'ProjectType', "MasterDatabase", "TL_Lake", "COMMENT", "DBA", "tags")
        
    def __init__(self, *args, **kwargs):
        readonly = kwargs.pop('readonly', False)
        manager = kwargs.pop('manager', False)        
        
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
                'RISK',
                Field('PRJ_DATE0', datadatepicker='datepicker'),                
                Field('PRJ_DATE1', datadatepicker='datepicker'),
                'ProjectType',
                'MasterDatabase',
                'TL_Lake',
                'DBA',
                'tags',
                HTML("""<p><em>(comma separated values)</em></p> """),
                Fieldset(
                      "Milestones",
                      'Approved',
                      'Conducted',
                      'DataScrubbed',
                      'DataMerged',
                      'SignOff'
                    ),
              ),
            ButtonHolder(
                Submit('submit', 'Submit')
            )
         )

        
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.readonly = readonly
        self.manager = manager

        if not manager:
            self.fields["Approved"].widget.attrs['disabled'] = True 
            self.fields["SignOff"].widget.attrs['disabled'] = True             
            self.fields["DataMerged"].widget.attrs['disabled'] = True                         
        
        if readonly:
            self.fields["PRJ_CD"].widget.attrs['readonly'] = True 


    def clean_Approved(self):
        '''if this wasn't a manager, reset the Approved value to the
        original (read only always returns false)'''
        if not self.manager:
            return self.instance.Approved
        else:
            return self.cleaned_data["Approved"]

    def clean_SignOff(self):
        '''if this wasn't a manager, reset the SignOff value to the
        original (read only always returns false)'''
        if not self.manager:
            return self.instance.SignOff
        else:
            return self.cleaned_data["SignOff"]

        
    def clean_DataMerged(self):
        '''if this wasn't a manager, reset the DataMerged value to the
        original (read only always returns false)'''
        if not self.manager:
            return self.instance.DataMerged
        else:
            return self.cleaned_data["DataMerged"]
        
    #def clean_Keywords(self):
        
        
            
    def clean_PRJ_CD(self):
        '''a clean method to ensure that the project code matches the
        given regular expression.  method also ensure that project
        code is unique.  If duplicate code is entered, an error
        message will be displayed including link to project with that
        project code.  The method only applies to new projects.  When
        editing a project, project code is readonly and does need to be checked.
        '''
        pattern  = "^[A-Z]{3}_[A-Z]{2}\d{2}_([A-Z]|\d){3}$"
        project_code =  self.cleaned_data["PRJ_CD"]

        if self.readonly == False: 
            if re.search(pattern, project_code):
                #make sure that this project code doesn't already exist:
                try:
                    proj = Project.objects.get(PRJ_CD=project_code)
                except Project.DoesNotExist:
                    proj = None
                if proj:
                    url = proj.get_absolute_url()
                    errmsg = "Project Code already exists (<a href='%s'>view</a>)." % url
                    raise forms.ValidationError(mark_safe(errmsg))
                else:
                    return project_code
            else:
                raise forms.ValidationError("Malformed Project Code.")
        else:
            #do nothing, just return the project code as is
            return project_code

    def clean(self):
        '''make sure that project start and end dates are in the same
        year, and that the start date occurs before the end date.
        Also make sure that the year in project code matches the start
        and end dates.'''

        cleaned_data = super(ProjectForm, self).clean()
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
        

    #def save(self):

        
class SisterProjectsForm(forms.Form):
    '''This project form is used to identify sister projects''' 

    sister = forms.BooleanField(
        label = "Sister:",
        required =False,
    )

    PRJ_CD = forms.CharField(
        widget = HyperlinkWidget,
        label = "Project Code",
        max_length = 13,
        required = False,
    )

    
    PRJ_NM = forms.CharField(
        widget = ReadOnlyText,
        label = "Project Name",
        required =False,
    )
    
    slug = forms.CharField(
        label = "slug",
        required =False,
    )
    

    PRJ_LDR = forms.CharField(
        widget = ReadOnlyText,
        label = "Project Leader",
        max_length = 80,
        required = False,
    )
    
    def __init__(self, *args, **kwargs):
        super(SisterProjectsForm, self).__init__(*args, **kwargs)
        self.fields["slug"].widget = forms.HiddenInput()

    def clean_PRJ_CD(self):
        '''return the original value of PRJ_CD'''
        return self.initial['PRJ_CD']
        
    def clean_PRJ_NM(self):
        '''return the original value of PRJ_NM'''
        return self.initial['PRJ_NM']
        
    def clean_PRJ_LDR(self):
        '''return the original value of PRJ_LDR'''
        return self.initial['PRJ_LDR']

    def save(self, *args, **kwargs):
        #family = kwargs.pop('family', None)
        parentslug = kwargs.pop('parentslug')
        parentProject = Project.objects.get(slug=parentslug)
        slug = self.cleaned_data['slug']
        #1. if sister was true and is now false, remove that
        # project from the family
        if (self.cleaned_data['sister']==False and
            self.initial['sister']==True):
            parentProject.delete_sister(slug)
        #2. if sister was false and is now true, add this project to the family.
        elif (self.cleaned_data['sister']==True and
            self.initial['sister']==False):
            parentProject.add_sister(slug)
        #do nothing
        else:
            pass














        
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




## 
## class AssignmentForm(forms.ModelForm):
##     '''A basic form for reporting requirements associated with a project'''
## 
##     required = forms.BooleanField(
##          label = "",
##          required =False,
##      )
## 
##     class Meta:
##         model=ProjectMilestones
##         fields = ('required', 'milestone')
##         widgets = {
##         #'required':forms.BooleanField(label=""),
##           'milestone':forms.HiddenInput(),        
##         }
##     
##     def clean_milestone(self):
##         '''return the original value of milestone'''
##         return self.instance.milestone
## 
## 
## 
##                 
## class CoreReportsForm(forms.Form):
##     '''Dynamically add checkbox widgets to a form depending on reports
##     identified as core.  This form is currently used to update
##     reporting requirements.  '''
##     
##     #pass
##     def __init__(self, *args, **kwargs):
##         self.reports = kwargs.pop('reports')
##         #self.project = kwargs.pop('project', None)
##         
##         super(CoreReportsForm, self).__init__(*args, **kwargs)
##         corereports = self.reports["core"]["reports"]
##         assigned = self.reports["core"]["assigned"]
##     
##         
##         self.fields['core'] = forms.MultipleChoiceField(
##             choices = corereports,
##             initial = assigned,
##             label = "",
##             required = True,
##             widget = forms.widgets.CheckboxSelectMultiple(),
##             )
## 
## 
## 
## class AdditionalReportsForm(forms.Form):
##     reports = Milestone.objects.filter(category='Custom')
##     #we need to convert the querset to a tuple of tuples
##     reports = tuple([(x[0], x[1]) for x in reports.values_list()])
##     ckboxes = forms.MultipleChoiceField(
##         choices = reports,
##         label = "",
##         required = True,
##         )
                
## 
## 
## ##  class NewProjectForm(forms.ModelForm):
## ##      formfield_callback = make_custom_datefield
## ##      class Meta:
## ##          model = Project
## ##          exclude = ("slug", "YEAR", "Owner",)
## 
