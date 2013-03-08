from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.context_processors import csrf
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory

from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator

from django.contrib.auth.models import User
from django.contrib.auth import logout

from pjtk2.models import Milestone, Project, Report, ProjectReports 
from pjtk2.models import TL_ProjType, TL_Database
#from pjtk2.forms import MilestoneForm
from pjtk2.forms import ProjectForm, ApproveProjectsForm, DocumentForm, ReportsForm 
from pjtk2.forms import AdditionalReportsForm, CoreReportsForm, AssignmentForm

import pdb

def is_manager(user):
    '''A simple little function to find out if the current user is a
    manager (or better)'''
    if user.groups.filter(name='manager').count()>0 | user.is_superuser:
        manager = True
    else:
        manager = False
    return(manager)

def canEdit(user, project):
    '''Another helper function to see if this user should be allowed
    to edit this project.  In order to edit the use must be either the
    project Owner, a manager or a superuser.'''
    canEdit = ((user.groups.filter(name='manager').count()>0) or 
                 (user.is_superuser) or 
                 (user.username == project.Owner.username))
    if canEdit:
        canEdit = True
    else:
        canEdit = False
    return(canEdit)
    
    
def initialReports(slug):

    '''A function that will add a record into "ProjectReports" for
    each of the core report for newly created projects'''

    project = Project.objects.get(slug=slug)
    corereports = Milestone.objects.filter(category='Core')

    for report in corereports:
        pr = ProjectReports(project=project, report_type = report)
        pr.save()
        

def get_assignments(slug):
    '''a function to get the core and custom reports currently
    assigned to a project.  It will return a two element dictionary
    containing the core and custom reports.  If this is a new project,
    all of the core elements will be populated by default as all of
    the deliverables will be required.'''
    
    #get a queryset of all reports we consider 'core'
    corereports = Milestone.objects.filter(category='Core')
    customreports = Milestone.objects.filter(category='Custom')

    #pdb.set_trace()
    
    #we need to convert the querset to a tuple of tuples
    corereports = tuple([(x[0], x[1]) for x in corereports.values_list()])
    customreports = tuple([(x[0], x[1]) for x in customreports.values_list()])    
    #see if there is a project associated with this slug, if so, get
    #the reports currently assigned to the project, if not return a
    #dictionary with all reports assigned
    project = Project.objects.filter(slug=slug)
    if project:
            core_assigned = ProjectReports.objects.filter(project__slug=
                            slug).filter(required=True).filter(report_type__category=
                            'Core')
            core_assigned = [x.report_type_id for x in list(core_assigned)]

            custom_assigned = ProjectReports.objects.filter(project__slug=
                            slug).filter(required=True).filter(report_type__category=
                            'Custom')
            custom_assigned = [x.report_type_id for x in list(custom_assigned)]
 
    else:
        core_assigned = [x[0] for x in corereports]
        custom_assigned = [x[0] for x in customreports]

    #put the reports and assigned reports in a dictionary    
    core = dict(reports=corereports, assigned=core_assigned)
    custom = dict(reports=customreports, assigned=custom_assigned)

    reports = dict(core=core, custom=custom)
    
    return(reports)

def get_assignments_with_paths(slug, core=True):
    '''function that will return a list of dictionaries for each of the
    reporting requirements.  each dictionary will indicate what the
    report is required, whether or not it has been requested for this
    project, and if it is available, a path to the associated
    report.'''
    
    project = Project.objects.get(slug=slug)

    if core:
        assignments = project.get_core_assignments()
    else:
        assignments = project.get_custom_assignments()
        
    assign_dicts = []
    for assignment in assignments:
        try:
            filepath = Report.objects.get(projectreport=assignment)
        except Report.DoesNotExist:
            filepath = None
        required = assignment.required
        report_type = assignment.report_type
        category = assignment.report_type.category
        assign_dicts.append(dict(
            required = required,
            category = category,
            report_type = report_type,
            filepath = filepath
        ))
    return assign_dicts
    
#===========================
#Generic Views    

class HomePageView(TemplateView):
    template_name = "index.html"


    
class ProjectList(ListView):
    queryset = Project.objects.all()
    template_name = "ProjectList.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectList, self).dispatch(*args, **kwargs)

    
project_list = ProjectList.as_view()


class ApprovedProjectsList(ListView):
    queryset = Project.objects.filter(Approved = True)
    template_name = "ApprovedProjectList.html"


    def get_context_data(self, **kwargs):
        context = super(ApprovedProjectsList, self).get_context_data(**kwargs)
        context['manager'] = is_manager(self.request.user)
        return context
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ApprovedProjectsList, self).dispatch(*args, **kwargs)

    
approved_projects_list = ApprovedProjectsList.as_view()


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

#===========================
# My application Views

@login_required            
def ProjectDetail(request, slug):
    '''View project details.'''
    
    project = get_object_or_404(Project, slug=slug)
    reports = get_assignments(slug)

    core = get_assignments_with_paths(slug)
    custom = get_assignments_with_paths(slug, core=False)

    user = User.objects.get(username__exact=request.user)       
    edit = canEdit(user, project)
    manager = is_manager(user)

    return render_to_response('projectdetail.html',
                              {'core':core,
                               'custom':custom,
                               'project':project,
                               'edit':edit,
                               'manager':manager
                               },
                              context_instance=RequestContext(request)
        )


    
def edit_project(request, slug):
    return crud_project(request, slug, action='Edit')

    
def copy_project(request, slug):
    return crud_project(request, slug, action='Copy')

    
def new_project(request):
    return crud_project(request, slug=None, action='New')

@login_required    
def crud_project(request, slug, action='New'):
    '''A view to create, copy and edit projects, depending on the
    value of 'action'.'''
    
    if slug:
        instance = Project.objects.get(slug=slug)
    else:
        instance = Project()

    #find out if the user is a manager or superuser, if so set manager
    #to true so that he or she can edit all fields.
    user = User.objects.get(username__exact=request.user)

    manager = is_manager(user)
        
    if request.method == 'POST': # If the form has been submitted...
        if action == 'Edit':
            form = ProjectForm(request.POST, instance=instance, 
                                   readonly=True, manager=manager)
        else:
            form = ProjectForm(request.POST, manager=manager)
                                  
        if form.is_valid():
            form = form.save(commit=False)
            form.Owner = request.user
            form.save()
            proj = Project.objects.get(slug=form.slug)
            if action != "Edit":
                #add a record for each report
                initialReports(form.slug)
            return HttpResponseRedirect(proj.get_absolute_url())            
        else:
            return render_to_response('ProjectForm.html',
                              {'form':form, 'action':action, 'project':instance},
                              context_instance=RequestContext(request))
    else:
        if action == "Edit":
            form = ProjectForm(instance=instance, readonly=True, manager=manager)
        elif action == "Copy":
            #make sure that project milestones are reset to false for new projects
            #instance = resetMilestones(instance)            
            instance.resetMilestones()            
            form = ProjectForm(instance=instance, manager=manager)            
        else:
            form = ProjectForm(instance=instance, manager=manager)                    
    return render_to_response('ProjectForm.html',
                              {'form':form, 'action':action, 'project':instance},
                              context_instance=RequestContext(request)
        )
        
@login_required
#@permission_required('Project.can_change_Approved')
def approveprojects(request):
    '''create a list of projects, project names and an
    approved/unapproved checkbox widget.'''

    if is_manager(request.user)==False:
        return HttpResponseRedirect(reverse('ApprovedProjectsList'))
    
    
    ProjectFormSet = modelformset_factory(Project, ApproveProjectsForm, extra=0)
    projects = Project.objects.all().filter(SignOff=False)

    if projects.count()==0:
        empty=True
    else:
        empty=False
    
    if request.method == 'POST':
        #pdb.set_trace()
        formset = ProjectFormSet(request.POST, queryset = projects)

        if formset.is_valid():
            # do something with the formset.cleaned_data
            formset.save()
            return HttpResponseRedirect(reverse('ApprovedProjectsList'))
        else:
            return render_to_response('ApproveProjects.html', 
                              {'formset': formset,
                               'empty':empty}, 
                               context_instance=RequestContext(request))
    else:
        formset = ProjectFormSet(queryset = projects)
    return render_to_response('ApproveProjects.html', 
                              {'formset': formset,
                               'empty':empty}, 
                               context_instance=RequestContext(request))

    
def report_milestones(request, slug):
    '''This function will render a form of requested reporting
    requirements for each project.  Used by managers to update
    reporting requirements for each project..'''

    project = Project.objects.get(slug = slug)    
    reports = get_assignments(slug) 

    if request.method=="POST":
        core =  ReportsForm(request.POST, project=project, reports=reports) 
        custom = ReportsForm(request.POST, project=project, reports = reports,
                             core=False)
        
        if core.is_valid() and custom.is_valid():
            core.save()            
            custom.save()
            
            return HttpResponseRedirect(project.get_absolute_url())
    else:
        core =  ReportsForm(project=project, reports = reports)
        custom =  ReportsForm(project=project, reports = reports, core=False)
        

    return render_to_response('reportform.html',
                              {'core':core,
                               'custom':custom,
                               'project':project
                               },
                              context_instance=RequestContext(request)
        )



def ReportUpload(request):
    pass
    

def uploadlist(request):
    '''An example view that illustrates how to handle uploading files.
    basic, but functional.'''
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            #pdb.set_trace()
            #newreport = Report(report_path = request.FILES['report_path'])
            #newreport.save()
            form.save()
            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('pjtk2.views.uploadlist'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    reports = Report.objects.all()
    # Render list page with the documents and the form
    return render_to_response(
        'upload_example.html',
        {'reports': reports, 'form': form},
        context_instance=RequestContext(request)
    )







    
#=============================================
#=============================================
from django.shortcuts import render
from forms import CrispyForm, ExampleForm
 
def crispy(request):
# This view is missing all form handling logic for simplicity of the example
    return render(request, 'crispyform.html', {'form': CrispyForm()})    

def crispy2(request):
# This view is missing all form handling logic for simplicity of the example
    return render(request, 'crispyform2.html', {'form': ExampleForm()})    




    

##def report_formset(request):
##    #  YOU ARE HERE
##    '''create a list of projects, project names and an
##    approved/unapproved checkbox widget.'''
##    ReportFormSet = formset_factory(CoreReportsForm2, extra=0)
##    projects = Project.objects.all()
##    reports = Milestone.objects.filter(category='Core')    
##    
##    initial = []
##
##    for project in projects:
##        assigned = ProjectReports.objects.filter(project__slug=
##                            project.slug).filter(report_type__category='Core')
##        assigned = assigned.values()
##        #assigned['PRJ_CD'] = project.PRJ_CD
##        #assigned['PRJ_CD'] = project.PRJ_NM
##        initial.append(assigned)
##    pdb.set_trace()
##        
##    if request.method == 'POST':
##        #pdb.set_trace()
##        formset = ReportFormSet(request.POST, reports=reports)
##        if formset.is_valid():
##            # do something with the formset.cleaned_data
##            #formset.save()
##            #orig will contain the origianl value of approved for each slug
##            #pdb.set_trace()
##            return HttpResponseRedirect(reverse('ApprovedProjectsList'))
##        else:
##            return render_to_response('manage_projects.html', 
##                              {'formset': formset}, 
##                               context_instance=RequestContext(request))
##    else:
##        formset = ReportFormSet(initial = initial, reports=reports)
##    return render_to_response('manage_projects.html', 
##                              {'formset': formset}, 
##                               context_instance=RequestContext(request))
##    




    

##  def project_reports(request, slug):
##      '''Another obsolete function.'''
##      project = get_object_or_404(Project, slug=slug)
##      #core =  CoreReportsForm()
##      #additional = AdditionalReportsForm()
##      return render_to_response('projectreports.html',
##                                {'core':core, 
##                                 'additional':additional,
##                                 'project':project},
##                                context_instance=RequestContext(request)
##          )
    


##  def update_assignments(request, slug): 
##  
##      '''render a form containing all of the assignments associated with
##      this project.'''  
##      
##      project = Project.objects.get(slug = slug) 
##      assignments = project.get_assignments()
##  
##      AssignmentFormSet = modelformset_factory(ProjectReports, AssignmentForm, extra=0)
##  
##      reports = get_assignments(slug)
##      #core =  CoreReportsForm(reports=reports)
##      #additional = AdditionalReportsForm()
##      #pdb.set_trace()
##      
##      if request.method == 'POST':
##          #pdb.set_trace()
##          #formset = AssignmentFormSet(request.POST, initial=initial)
##          formset = AssignmentFormSet(request.POST, initial = assignments)
##  
##          if formset.is_valid():
##              # do something with the formset.cleaned_data
##              formset.save()
##              return HttpResponseRedirect(project.get_absolute_url())
##          else:
##              return render_to_response('scratch.html', 
##                                {'formset': formset}, 
##                                 context_instance=RequestContext(request))
##      else:
##          formset = AssignmentFormSet(queryset = assignments)
##          #formset = AssignmentFormSet(initial=initial)
##          return render_to_response('scratch.html', 
##                                {'formset': formset,
##      #'core':core, 
##      #                           'additional':additional,
##                                }, 
##                                 context_instance=RequestContext(request))
##  



##  def resetMilestones(project):
##      '''a function to make sure that all of the project milestones are
##      set to zero. Used when copying an existing project - we don't want
##      to copy its milestones too'''
##      project.Approved = False
##      project.Conducted = False
##      project.DataScrubbed = False
##      project.DataMerged = False                        
##      project.SignOff = False
##      return project
