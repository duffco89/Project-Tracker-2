from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.context_processors import csrf
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory

from pjtk2.models import Milestone, Project, Report, ProjectReports 
from pjtk2.models import TL_ProjType, TL_Database
#from pjtk2.forms import MilestoneForm
from pjtk2.forms import ProjectForm, ProjectForm2, DocumentForm 
from pjtk2.forms import AdditionalReportsForm, CoreReportsForm

import pdb


def resetMilestones(project):
    '''a function to make sure that all of the project milestones are
    set to zero. Used when copying an existing project - we don't want
    to copy its milestones too'''
    project.Approved = False
    project.Conducted = False
    project.DataScrubbed = False
    project.DataMerged = False                        
    project.SignOff = False
    return project

def initialReports(slug):

    '''A function that will add a record into "ProjectReports" for
    each of the core report for newly created projects'''

    project = Project.objects.get(slug=slug)
    corereports = Milestone.objects.filter(category='Core')

    for report in corereports:
        pr = ProjectReports(project=project, report_type = report)
        pr.save()
        

def get_reports(slug):
    '''a function to get the core and custom reports currently
    assigned to a project.  It will return a two element dictionary
    containing the core and custom reports.  If this is a new project,
    all of the core elements will be populated by default as all of
    the deliverables will be required.'''

    #get a queryset of all reports we consider 'core'
    corereports = Milestone.objects.filter(category='Core')
    customreports = Milestone.objects.filter(category='Custom')
    #we need to convert the querset to a tuple of tuples
    corereports = tuple([(x[0], x[1]) for x in corereports.values_list()])
    customreports = tuple([(x[0], x[1]) for x in customreports.values_list()])    
    #see if there is a project associated with this slug, if so, get
    #the reports currently assigned to the project, if not return a
    #dictionary with all reports assigned
    project = Project.objects.filter(slug=slug)
    if project:
            core_assigned = ProjectReports.objects.filter(project__slug=
                            slug).filter(report_type__category='Core')
            core_assigned = [x.report_type_id for x in list(core_assigned)]

            custom_assigned = ProjectReports.objects.filter(project__slug=
                            slug).filter(report_type__category='Custom')
            custom_assigned = [x.report_type_id for x in list(custom_assigned)]
 
    else:
        core_assigned = [x[0] for x in corereports]
        custom_assigned = [x[0] for x in customreports]

    #put the reports and assigned reports in a dictionary    
    core = dict(reports=corereports, assigned=core_assigned)
    custom = dict(reports=customreports, assigned=custom_assigned)

    reports = dict(core=core, custom=custom)
    
    return(reports)

#===========================
#Generic Views    



class HomePageView(TemplateView):
    template_name = "index.html"

class ProjectList(ListView):
    queryset = Project.objects.all()
    template_name = "ProjectList.html"

project_list = ProjectList.as_view()


class ApprovedProjectsList(ListView):
    queryset = Project.objects.filter(Approved = True)
    template_name = "ApprovedProjectList.html"

approved_projects_list = ApprovedProjectsList.as_view()
    
        
def ProjectDetail(request, slug):
    '''View project details.'''
    #pdb.set_trace()
    
    project = get_object_or_404(Project, slug=slug)
    reports = get_reports(slug)
    
    if request.method=="POST":
        core =  CoreReportsForm(request.POST, reports=reports)

        if core.is_valid():
            #form.save()
            return HttpResponseRedirect(reverse('ProjectList'))
    else:
        core =  CoreReportsForm(reports=reports)
    #reports = MilestoneForm()

    #additional = AdditionalReportsForm()

    return render_to_response('projectdetail.html',
                              {'core':core,
                               #'additional':additional,
                               'project':project
                               },
                              context_instance=RequestContext(request)
        )

    
def edit_project(request, slug):
    return crud_project(request, slug, action='Edit')

    
def copy_project(request, slug):
    return crud_project(request, slug, action='Copy')

    
def new_project(request):
    return crud_project(request, slug=None, action='New')

    
def crud_project(request, slug, action='New'):
    '''A view to create, copy and edit projects, depending on the
    value of 'action'.'''
    
    if slug:
        instance = Project.objects.get(slug=slug)
    else:
        instance = Project()

        #if request.user.manager == True:    
    manager = True
    #else:
    #manager = False
        
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
            instance = resetMilestones(instance)            
            form = ProjectForm(instance=instance, manager=manager)            
        else:
            form = ProjectForm(instance=instance, manager=manager)                    
    return render_to_response('ProjectForm.html',
                              {'form':form, 'action':action, 'project':instance},
                              context_instance=RequestContext(request)
        )
        

def project_formset(request):
    '''create a list of projects, project names and an
    approved/unapproved checkbox widget.'''
    ProjectFormSet = modelformset_factory(Project, ProjectForm2, extra=0)
    projects = Project.objects.all()
    
    if request.method == 'POST':
        #pdb.set_trace()
        formset = ProjectFormSet(request.POST, queryset = projects)

        if formset.is_valid():
            # do something with the formset.cleaned_data
            formset.save()
            ###orig will contain the origianl value of approved for each slug
            ##original = Project.objects.only('slug','Approved')
            ##instances = formset.save(commit=False)
            ###pdb.set_trace()
            ##for obj in instances:                
            ##    #THIS NEEDS TO BE IMPROVED - ONLY UPDATE THOSE RECORDS
            ##    #THAT HAVE BEEN CHANGED
            ##    #think about some quick set operations
            ##    orig = original.filter(slug=obj.slug).values('Approved')
            ##    if orig != obj.Approved:                    
            ##        Project.objects.filter(slug=obj.slug).update(Approved=obj.Approved)
            return HttpResponseRedirect(reverse('ApprovedProjectsList'))
        else:
            return render_to_response('manage_projects.html', 
                              {'formset': formset}, 
                               context_instance=RequestContext(request))
    else:
        formset = ProjectFormSet(queryset = projects)
    return render_to_response('manage_projects.html', 
                              {'formset': formset}, 
                               context_instance=RequestContext(request))

##  def project_milestones(request, slug):
##      '''Another obsolete function.'''
##      project = get_object_or_404(Project, slug=slug)
##      core =  CoreReportsForm()
##      additional = AdditionalReportsForm()
##      return render_to_response('projectdetail.html',
##                                {'core':core, 'additional':additional,
##                                 'project':project},
##                                context_instance=RequestContext(request)
##          )
    


def ReportUpload(request):
    pass


def uploadlist(request):
    '''An example view that illustrates how to handle uploading files.
    basic, but functional.'''
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():

            newreport = Report(report_path = request.FILES['report_path'])
            #pdb.set_trace()
            newreport.save()

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




    
def report_milestones(request, slug):
    '''This function will render a form of requestedreporting requirements for
    each project.'''
    #slug = "lha_ia13_abc"
    reports = get_reports(slug) 
    project = Project.objects.get(slug = slug)
    #project = project.value("PRJ_CD", "PRJ_NM")
    #project = dict(PRJ_CD="LHA_IA13_ABC", PRJ_NM="Netting in Bobwho Bay")
    
    if request.method=="POST":
        core =  CoreReportsForm(request.POST, reports=reports, 
                                project=project)
        #pdb.set_trace()
        if core.is_valid():
            #form.save()
            return HttpResponseRedirect(reverse('ProjectList'))
    else:
        core =  CoreReportsForm(reports = reports, project=project)
    #reports = MilestoneForm()
    #additional = AdditionalReportsForm()

    return render_to_response('reportform.html',
                              {'core':core,
                               #'additional':additional
                               },
                              context_instance=RequestContext(request)
        )


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
