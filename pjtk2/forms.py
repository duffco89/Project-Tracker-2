# E1101 - Class 'whatever' has no 'something' member
# E1120 - No value passed for parameter 'cls' in function call
#pylint: disable=E1101, E1120

import datetime
import pytz
import re
import hashlib


from django import forms
from django.contrib.auth.models import User
from django.forms.formsets import BaseFormSet
from django.forms import ModelChoiceField, CharField
from django.forms.widgets import (CheckboxSelectMultiple, Select,
                                  CheckboxInput, mark_safe)

#from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from olwidget.fields import MapField, EditableLayerField

from itertools import chain

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Submit, Layout, Fieldset, Field, ButtonHolder,
                                 Div)
from crispy_forms.bootstrap import PrependedText

from taggit.forms import *
from pjtk2.models import (Milestone, Project, ProjectMilestones, Report,
                          ProjectType, Database, Lake, Messages2Users,
                          AssociatedFile)


#==================================
#  WIDGETS

def make_custom_datefield(fld, **kwargs):
    '''from: http://strattonbrazil.blogspot.ca/2011/03/
                 using-jquery-uis-date-picker-on-all.html'''
    from django.db import models
    formfield = fld.formfield(**kwargs)
    if isinstance(fld, models.DateField):
        formfield.widget.format = '%m/%d/%Y'
        formfield.widget.attrs.update({'class':'datepicker'})
    return formfield


class UserModelChoiceField(ModelChoiceField):
    '''a custom model choice widget for user objects.  It will
    display user first and last name in list of available choices
    (rather than their official user name). modified from
    https://docs.djangoproject.com/en/dev/ref/forms/fields/#modelchoicefield.
    '''
    def label_from_instance(self, obj):
        if obj.first_name:
            label = "{0} {1}".format(obj.first_name, obj.last_name)
        else:
            label = obj.__str__()
        return label


class UserReadOnlyText(forms.TextInput):
    '''a custom readonly text widget for user objects.  It will
    displace user first and last name of user if available, otherwise
    username.
    '''
    input_type = 'text'
    def render(self, name, value, attrs=None):
        user = User.objects.get(id=value)
        if user.first_name:
            value = "{0} {1}".format(user.first_name, user.last_name)
        else:
            value = str(user)
        return value


class ReadOnlyText(forms.TextInput):
    '''from:
    http://stackoverflow.com/questions/1134085/
                rendering-a-value-as-text-instead-of-field-inside-a-django-form
    modified to get milestone labels if name starts with 'projectmilestone'
    '''
    input_type = 'text'
    def render(self, name, value, attrs=None):
        if name.startswith('projectmilestone'):
            value = Milestone.objects.get(id=value).label
        elif value is None:
            value = ''
        return str(value)


class HyperlinkWidget(forms.Widget):
    """This is a widget that will insert a hyperlink to a project
    detail page in a form set."""

    def __init__(self, text, url='#',*args, **kwargs):
        self.url = url
        self.text = text
        super(HyperlinkWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        output = []
        output.append('<a href="%s">%s</a>' % (self.url, self.text))
        return mark_safe(u''.join(output))


class CheckboxSelectMultipleWithDisabled(CheckboxSelectMultiple):
    """Subclass of Django's checkbox select multiple widget that allows
    disabling checkbox-options.  To disable an option, pass a dict
    instead of a string for its label, of the form: {'label': 'option
    label', 'disabled': True}
    """
    #from http://djangosnippets.org/snippets/2786/
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        #output = [u'<ul>']
        output = [u'']
        # Normalize to strings
        #str_values = set([force_unicode(v) for v in value])
        str_values = set([v for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices,
                                                               choices)):
            if final_attrs.has_key('disabled'):
                del final_attrs['disabled']
            if isinstance(option_label, dict):
                if dict.get(option_label, 'disabled'):
                    final_attrs = dict(final_attrs, disabled = 'disabled' )
                option_label = option_label['label']
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''
            chbox = CheckboxInput(final_attrs,
                               check_test=lambda value: value in str_values)
            #option_value = force_unicode(option_value)
            rendered_cb = chbox.render(name, option_value)
            #option_label = conditional_escape(force_unicode(option_label))
            option_label = conditional_escape(option_label)
            output.append(u'<label%s>%s %s</label>'
                          % (label_for, rendered_cb, option_label))
        #output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))

#==================================
#  FORMS


class NoticesForm(forms.Form):
    '''This form is used to display un-read messages.  Once read, the user
    can click the read box and submit the form to remove them from the
    que.'''

    read = forms.BooleanField(
        label="Read:",
        required=False,
    )

    prj_nm = forms.CharField(
        widget=ReadOnlyText,
        label="Project Name",
        required=False,
    )

    msg_id = forms.CharField(
        label="msg_id",
        required=False,
    )

    user_id = forms.CharField(
        label="user_id",
        required=False,
    )

    msg = forms.CharField(
        widget=ReadOnlyText,
        label="Message",
        max_length=80,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(NoticesForm, self).__init__(*args, **kwargs)

        self.fields["msg_id"].widget = forms.HiddenInput()
        self.fields["user_id"].widget = forms.HiddenInput()
        self.prj_cd = kwargs['initial'].get('prj_cd', None)
        self.url = kwargs['initial'].get('url', None)

        #use a hyperlink widget for the project code
        self.fields.update({"prj_cd": forms.CharField(
            widget=HyperlinkWidget(url=self.url,
                                   text=self.prj_cd),
            label="Project Code",
            max_length=13,
            required=False)})


        #snippet makes sure that Approved appears first
        self.fields.keyOrder = ['read', 'prj_cd', 'prj_nm', 'msg',
                                'msg_id', 'user_id']

    def save(self, *args, **kwargs):

        if self.cleaned_data['read'] is True:
            now = datetime.datetime.now(pytz.utc)
            msg_id = self.initial['msg_id']
            user_id = self.initial['user_id']

            message2user = Messages2Users.objects.filter(id=msg_id,
                                                         user__id=user_id)
            message2user.update(read=now)


class ApproveProjectsForm(forms.ModelForm):
    '''This project form is used for view to approve/unapprove
    multiple projects.'''

    prj_nm = forms.CharField(
        widget = ReadOnlyText,
        label = "Project Name",
        required =False,
    )

    #prj_ldr = forms.CharField(
    #    label = "Project Leader",
    #    max_length = 80,
    #    required = False,
    #)


    class Meta:
        model = Project
        fields = ('prj_cd', 'prj_nm', 'prj_ldr', 'project_type')

    def __init__(self, *args, **kwargs):
        super(ApproveProjectsForm, self).__init__(*args, **kwargs)

        self.fields['Approved'] = forms.BooleanField(
            label = "Approved",
            required =False,
            initial = self.instance.is_approved(),
        )

        self.fields["prj_ldr"].widget = forms.HiddenInput()

        self.fields['prj_ldr_label'] = forms.CharField(
            widget = ReadOnlyText,
            label = "Project Leader",
            required =False,
            initial = "{0} {1}".format(self.instance.prj_ldr.first_name,
                                       self.instance.prj_ldr.last_name)
        )


        self.fields["project_type"].widget = forms.HiddenInput()

        self.fields['project_type_label'] = forms.CharField(
            widget = ReadOnlyText,
            label = "Project Type",
            required =False,
            initial = self.instance.project_type
        )


        self.fields.update({"prj_cd":forms.CharField(
            widget = HyperlinkWidget(
                             url = self.instance.get_absolute_url(),
                             text = self.instance.prj_cd),
            label = "Project Code",
            max_length = 12,
            required = False,
        )
        ,})

        #snippet makes sure that Approved appears first
        self.fields.keyOrder = ['Approved','prj_cd', 'prj_nm',
                                'project_type_label', 'prj_ldr_label']


    def clean_prj_cd(self):
        '''return the original value of prj_cd'''
        return self.instance.prj_cd

    def clean_prj_nm(self):
        '''return the original value of prj_nm'''
        return self.instance.prj_nm

    def clean_project_type(self):
        '''return the original value of prj_nm'''
        return self.instance.project_type

    def clean_prj_ldr(self):
        '''return the original value of prj_ldr'''
        return self.instance.prj_ldr

    def clean_prj_ldr_label(self):
        '''return the original value of prj_ldr_label none - make sure
        nothing is returned
        '''
        return None

    def save(self, commit=True):
        if self.has_changed:
            if self.cleaned_data['Approved']:
                self.instance.approve()
            else:
                self.instance.unapprove()
        return super(ApproveProjectsForm, self).save(commit)



class ReportsForm(forms.Form):
    '''This form is used to update reporting requirements for a
    particular project.  Checkbox widgets are dynamically added to the
    form depending on reports identified as core plus any additional
    custom reports requested by the manager.'''

    def __init__(self, *args, **kwargs):
        self.milestones = kwargs.pop('reports')
        self.what = kwargs.pop('what', 'Core')
        self.project = kwargs.pop('project', None)

        super(ReportsForm, self).__init__(*args, **kwargs)

        reports = self.milestones[self.what]["milestones"]
        assigned = self.milestones[self.what]["assigned"]

        self.fields[self.what] = forms.MultipleChoiceField(
            choices=reports,
            initial=assigned,
            label="",
            required=False,
            widget=forms.widgets.CheckboxSelectMultiple(),
            )


    def save(self):
        '''in order for a milestone to be associated with a project, it must
        have a record in ProjectMilestones with required=True.  There
        are three logic paths we have to cover:\n
        - records in ProjectMilestones that need to have required set to True
        - records in ProjectMilestones that need to have required set to False
        - records tht need to be added to ProjectMilestones
        '''

        cleaned_data = self.cleaned_data
        project = self.project
        what = self.what

        existing = project.get_milestone_dicts()[what]['assigned']
        values = list(cleaned_data.values())[0]
        cleaned_list = [int(x) for x in values]

        #these are the milestones that are existing but not in cleaned_data
        turn_off = list(set(existing) - set(cleaned_list))
        #these are the milestones that were not assigned but they are
        #now in cleaned data.
        turn_on = list(set(cleaned_list) - set(existing))

        #turn OFF any ProjectMilestones that are not in cleaned data
        ProjectMilestones.objects.filter(project = project,
                  milestone__id__in=turn_off).update(required=False)

        #turn on any ProjectMilestones that are in cleaned data
        ProjectMilestones.objects.filter(project = project,
                  milestone__id__in=turn_on).update(required=True)

        #new records can be identified as milestone id's in cleaned
        #data that are not in ProjectMilestone
        projmst = ProjectMilestones.objects.filter(
            project=project).values('milestone__id')
        projmst = [x['milestone_id'] for x in projmst.values()]

        new = list(set(cleaned_list) - set(projmst))

        #now loop over new milestones adding a new record to ProjectReports for
        #each one with required=True
        if new:
            for milestone in new:
                ProjectMilestones.objects.create(project=project,
                                              required=True,
                                              milestone_id=milestone)


#class ReportUploadFormSet(BaseFormSet):
#    '''modified from
#    here:http://stackoverflow.com/questions/
#                     5426031/django-formset-set-current-user
#    allows additional parameters to be passed to formset.  Project and
#    user are required to upload reports.
#
#    This formset is used to upload the reports for a particular
#    project.  It will generate one reportUploadForm for each reporting
#    requirement (all core reports plus any additional reports that
#    have been requested).
#
#    Additionally, the project and user id will associated with each
#    form so that they can be appended and uploaded properly.
#    '''
#    def __init__(self, *args, **kwargs):
#        self.project = kwargs.pop('project', None)
#        self.user = kwargs.pop('user', None)
#        super(ReportUploadFormSet, self).__init__(*args, **kwargs)
#        for form in self.forms:
#            form.empty_permitted = False
#
#    def _construct_forms(self):
#        if hasattr(self,"_forms"):
#            return self._forms
#        self._forms = []
#        for i in range(self.total_form_count()):
#            self._forms.append(self._construct_form(i,
#                                                   project=self.project,
#                                                   user=self.user))
#        return self._forms
#
#    forms = property(_construct_forms)



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

        now = datetime.datetime.now(pytz.utc)

        if ('report_path' in self.changed_data and
                          self.cleaned_data['report_path']):

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

            report_path = self.cleaned_data['report_path']
            report_hash = hashlib.sha1(str(report_path).encode('utf-8')).hexdigest()

            newReport = Report(
                    report_path = report_path,
                    uploaded_by = self.user,
                    report_hash = report_hash
                )

            newReport.save()
            #add the m2m record for this projectreport
            newReport.projectreport.add(projectreport)

            projectreport.completed = now
            projectreport.save()

            #if this a presentation or summary report, see if
            #this project has any sister projects.  If so, add an m2m
            #for each one so this document is associated with them
            #too.
            #TODO: figure out how to handle sisters
            #that are adopted or dis-owned - how do we synchronize
            #existing files?

            sisters = self.project.get_sisters()

            shared_milestones = Milestone.objects.shared()
            shared_labels = [x.label for x in shared_milestones]

            #common = str(self.clean_milestone()) in ["Proposal Presentation",
            #                                    "Completetion Presentation",
            #                                    "Summary Report",]
            common = str(self.clean_milestone()) in shared_labels

            if sisters and common:
                for sister in sisters:
                    projreport, created = ProjectMilestones.objects.get_or_create(
                        project=sister, milestone=self.clean_milestone())
                    try:
                        oldReport = Report.objects.get(projectreport=projreport,
                                                       current=True)
                        oldReport.current = False
                        oldReport.save()
                    except Report.DoesNotExist:
                        oldReport = None
                    #add the m2m relationship for the sister
                    newReport.projectreport.add(projreport)
                    projectreport.completed = now
                    projectreport.save()






class ProjectForm(forms.ModelForm):
    '''This a form for new projects using crispy-forms and including
    cleaning methods to ensure that project code is valid, dates agree
    and ....  for a new project, we need project code, name, comment,
    leader, start date, end date, database, project type,'''

    prj_nm = forms.CharField(
        label="Project Name:",
        required=True,
    )

    prj_cd = forms.CharField(
        label="Project Code:",
        max_length=12,
        required=True,
    )

    prj_ldr = UserModelChoiceField(
        label="Project Leader:",
        queryset=User.objects.filter(is_active=True).\
        order_by('first_name', 'last_name'),
        required=True,
    )

    field_ldr = UserModelChoiceField(
        label="Field Leader:",
        queryset=User.objects.filter(is_active=True),
        required=False,
    )

    owner = UserModelChoiceField(
        label="Data Custodian:",
        queryset=User.objects.filter(is_active=True),
        required=False,
    )

    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'input-xxlarge', 'rows': 20, 'cols': 60}),
        label="Brief Project Description:",
        required=True,
        )

    risk = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'input-xxlarge', 'rows': 20, 'cols': 60}),
        label="Risks associated with not running project:",
        required=False,
        )

    prj_date0 = forms.DateField(
        label="Start Date:",
        required=True,
        input_formats=["%d/%m/%Y","%Y-%m-%d"],
    )

    prj_date1 = forms.DateField(
        label="End Date:",
        required=True,
        input_formats=["%d/%m/%Y", "%Y-%m-%d"],
    )

    project_type = forms.ModelChoiceField(
        label="Project Type:",
        queryset=ProjectType.objects.all().order_by('project_type'),
        required=True,
    )

    funding = forms.CharField(
        label = 'Funding Source:',
        widget=Select(choices=Project.FUNDING_CHOICES),
        required=False)

    salary = forms.DecimalField(required=False, decimal_places=2)
    odoe = forms.DecimalField(required=False, decimal_places=2)

    master_database = forms.ModelChoiceField(
        label="Master Database:",
        queryset=Database.objects.all(),
        required=True,
    )

    lake = forms.ModelChoiceField(
        label="Lake:",
        queryset=Lake.objects.all(),
        required=True,
    )

    dba = forms.ModelChoiceField(
        label="DBA:",
        #TODO - change this from superuser to groups__contain='dba'
        queryset=User.objects.filter(is_superuser=True),
        required=True,
    )

    tags = TagField(
        label="Keywords:",
        required=False,
        help_text="<em>(comma separated values)</em>")

    class Meta:
        model = Project
        fields = ("prj_nm", "prj_ldr", "field_ldr", "owner","prj_cd",
                  "prj_date0", "prj_date1", "risk", 'project_type',
                  "master_database", "lake", "comment", "dba", "tags",
                  'salary', 'odoe', 'funding')

    def __init__(self, *args, **kwargs):
        readonly = kwargs.pop('readonly', False)
        manager = kwargs.pop('manager', False)

        milestones = kwargs.pop('milestones', None)

        self.helper = FormHelper()
        self.helper.form_id = 'ProjectForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.add_input(Submit('submit', 'Submit'))

        self.helper.layout = Layout(
            Div(
                Fieldset(
                    'Project Elements',
                    'prj_nm',
                    'prj_cd',
                    'prj_ldr',
                    'field_ldr',
                    'owner',
                    'comment',
                    'risk',
                    Field('prj_date0', placeholder = "dd/mm/yyyy",
                          css_class='datepicker'),
                    Field('prj_date1', placeholder = "dd/mm/yyyy",
                          css_class='datepicker'),
                    'project_type',
                    'funding',
                     PrependedText('salary', '$'),
                     PrependedText('odoe', '$'),
                    'master_database',
                    'lake',
                    'dba',
                    'tags'
                )),
         )

        super(ProjectForm, self).__init__(*args, **kwargs)
        self.readonly = readonly
        self.manager = manager

        if readonly:
            self.fields["prj_cd"].widget.attrs['readonly'] = True
            #this is an edit so our project lead could be anyone:
            self.fields["prj_ldr"].queryset =  User.objects.order_by(
                'first_name', 'last_name').all()
            self.fields["field_ldr"].queryset = User.objects.order_by(
            'first_name', 'last_name').all()
            self.fields["owner"].queryset = User.objects.order_by(
                'first_name', 'last_name').filter(is_active=True).all()

        if milestones:
            if self.manager is True:
                choices = [(x.id, {'label': x.milestone.label,
                                   'disabled': False})
                           for x in milestones]
            else:
                choices = [(x.id, {'label': x.milestone.label,
                                   'disabled': x.milestone.protected})
                           for x in milestones]

            # *** NOTE ***
            #'completed' must be a list of values that match the choices (above)
            completed = [x.id for x in milestones if x.completed is not None]
            self.fields.update(
                {"milestones": forms.MultipleChoiceField(
                    widget=CheckboxSelectMultipleWithDisabled(),
                    choices=choices,
                    label="",
                    initial=completed,
                    required=False,
            ),})
            self.helper.layout[0].extend(
                [Div(Fieldset(
                    'Milestones',
                    #'milestones'
                    Field('milestones',
                          template='pjtk2/_MultipleSelectwDisable.html')
                ), css_class="row")])


    def clean_approved(self):
        '''if this wasn't a manager, reset the Approved value to the
        original (read only always returns false)'''
        if self.manager:
            return self.cleaned_data["Approved"]
        else:
            return self.instance.Approved


    def clean_prj_cd(self):
        '''a clean method to ensure that the project code matches the
        given regular expression.  method also ensure that project
        code is unique.  If duplicate code is entered, an error
        message will be displayed including link to project with that
        project code.  The method only applies to new projects.  When
        editing a project, project code is readonly and does need to be checked.
        '''
        pattern  = r"^[A-Z]{3}_[A-Z]{2}\d{2}_([A-Z]|\d){3}$"
        project_code =  self.cleaned_data["prj_cd"]

        if self.readonly == False:
            if re.search(pattern, project_code):
                #make sure that this project code doesn't already exist:
                try:
                    proj = Project.objects.get(prj_cd=project_code)
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

    def clean_tags(self):
        """
        Force all tags to lowercase.
        modified from:http://stackoverflow.com/questions/25676952/
        """
        tags = self.cleaned_data.get('tags', None)
        if tags:
            tags = list(set([t.lower() for t in tags]))

        return tags


    def clean(self):
        '''make sure that project start and end dates are in the same
        year, and that the start date occurs before the end date.
        Also make sure that the year in project code matches the start
        and end dates.'''

        cleaned_data = super(ProjectForm, self).clean()
        start_date = cleaned_data.get('prj_date0')
        end_date = cleaned_data.get('prj_date1')
        project_code = cleaned_data.get('prj_cd')

        #if this is not a manager, the protected fields will not be
        #included in the cleaned data for the milestones - we need to
        #add them back in
        form_ms = cleaned_data.get('milestones')
        if form_ms:
            if not self.manager:
                ms = self.instance.get_milestones()
                protected_ms = ([x.id for x in ms if x.milestone.protected
                                 and x.completed is not None])
                cleaned_data['milestones'].extend(protected_ms)

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



class SisterProjectsForm(forms.Form):
    '''This project form is used to identify sister projects'''

    sister = forms.BooleanField(
        label="Sister:",
        required=False,
    )

    prj_nm = forms.CharField(
        widget=ReadOnlyText,
        label="Project Name",
        required=False,
    )

    slug = forms.CharField(
        label="slug",
        required=False,
    )

    prj_ldr = forms.CharField(
        widget=ReadOnlyText,
        label="Project Leader",
        max_length=80,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(SisterProjectsForm, self).__init__(*args, **kwargs)

        self.fields["slug"].widget = forms.HiddenInput()
        self.prj_cd = kwargs['initial'].get('prj_cd', None)
        self.url = kwargs['initial'].get('url', None)

        #use a hyperlink widget for the project code
        self.fields.update({"prj_cd": forms.CharField(
            widget=HyperlinkWidget(url=self.url,
                                   text=self.prj_cd),
            label="Project Code", max_length=13, required=False,
        )})

        #snippet makes sure that Approved appears first
        self.fields.keyOrder = ['sister', 'prj_cd', 'prj_nm',
                                'prj_ldr', 'slug']


    def clean_prj_cd(self):
        '''return the original value of prj_cd'''
        return self.initial['prj_cd']

    def clean_prj_nm(self):
        '''return the original value of prj_nm'''
        return self.initial['prj_nm']

    def clean_prj_ldr(self):
        '''return the original value of prj_ldr'''
        return self.initial['prj_ldr']

    def save(self, *args, **kwargs):
        #family = kwargs.pop('family', None)
        parentslug = kwargs.pop('parentslug')
        parentProject = Project.objects.get(slug=parentslug)
        slug = self.cleaned_data['slug']
        #1. if sister was true and is now false, remove that
        # project from the family
        if (self.cleaned_data['sister'] is False and
              self.initial['sister'] is True):
            parentProject.delete_sister(slug)
        #2. if sister was false and is now true, add this project to the family.
        elif (self.cleaned_data['sister'] is True and
              self.initial['sister'] is False):
            parentProject.add_sister(slug)
        #do nothing
        else:
            pass


class AssociatedFileUploadForm(forms.Form):
    '''A simple little form for uploading files one at a time.'''

    file_path = forms.FileField(
        label = "File",
        required =False,
        )

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        self.user = kwargs.pop('user')
        super(AssociatedFileUploadForm, self).__init__(*args, **kwargs)
        self.fields["file_path"].widget.attrs['size'] = "40"
        self.fields["file_path"].widget.attrs['class'] = "fileinput"


    def save(self):
        '''fill in the project, user, uploaded time and file hash when we save
        it.'''

        newReport = AssociatedFile(
            project = self.project,
            file_path = self.cleaned_data['file_path'],
            uploaded_by = self.user,
            hash = hashlib.sha1(
                str(self.cleaned_data['file_path'])).hexdigest()
            )
        newReport.save()


class GeoForm(forms.Form):
    """Load a map centered over Lake Huron. """

    selection = MapField([
        EditableLayerField({
            'geometry': 'polygon',
            'is_collection': False,
            #'name': 'selection',
        })],

         options= {
             'default_lat': 45,
             'default_lon': -81.7,
             'default_zoom':7,
             'map_div_style': {'width': '650px', 'height': '600px'},
          }

        )

    project_types = forms.ModelMultipleChoiceField(
        (ProjectType.objects.filter(field_component=True).
         order_by('project_type')),
        required=False,
        widget=forms.CheckboxSelectMultiple(), label='Project Type')

    first_year = forms.IntegerField(required=False)
    last_year = forms.IntegerField(required=False)
