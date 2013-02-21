from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.context_processors import csrf
from django.views.generic import ListView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from pjtk2.models import Milestone, Project, Report, ProjectReports 
from pjtk2.models import TL_ProjType, TL_Database
#from pjtk2.forms import MilestoneForm
from pjtk2.forms import AdditionalReportsForm, CoreReportsForm, NewProjectForm, DocumentForm 

import pdb


class ProjectList(ListView):
    queryset = Project.objects.all()
    template_name = "ProjectList.html"

project_list = ProjectList.as_view()


def ReportMilestones(request):
    if request.method=="POST":
        core =  CoreReportsForm(request.POST)
        #pdb.set_trace()
        if core.is_valid():
            #form.save()
            return HttpResponseRedirect(reverse('ProjectList'))
    else:
        core =  CoreReportsForm()
    #reports = MilestoneForm()

    #additional = AdditionalReportsForm()

    return render_to_response('simpleform.html',
                              {'core':core,
                               #'additional':additional
                               },
                              context_instance=RequestContext(request)
        )


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

        
def ViewReports(request, slug):
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

    return render_to_response('simpleform.html',
                              {'core':core,
                               #'additional':additional,
                               'project':project
                               },
                              context_instance=RequestContext(request)
        )

def edit_project(request,slug):
    pass
    
def copy_project(request,slug):
    project = get_object_or_404(Project, slug=slug)
    if project:
        data = dict(
                PRJ_CD = project.PRJ_CD,
                PRJ_NM = project.PRJ_NM,
                PRJ_LDR = project.PRJ_LDR,
                PRJ_DATE0 = project.PRJ_DATE0,                
                PRJ_DATE1 = project.PRJ_DATE1,
                COMMENT = project.COMMENT,
                ProjectType = project.ProjectType.id,
                MasterDatabase = project.MasterDatabase.id,
            )

    if request.method == 'POST': # If the form has been submitted...
        form = NewProjectForm(data=request.POST, user=request.user)
        if form.is_valid():
            new_project = form.save()
            return HttpResponseRedirect(new_project.get_absolute_url())
        else:
            return render_to_response('ProjectForm.html',
                              {'form':form},
                              context_instance=RequestContext(request))
    else:
        form = NewProjectForm(data = data, user=request.user) 
    return render_to_response('ProjectForm.html',
                              {'form':form},
                              context_instance=RequestContext(request)
        )
    

def project_milestones(request, slug):
    project = get_object_or_404(Project, slug=slug)
    core =  CoreReportsForm()
    additional = AdditionalReportsForm()
    return render_to_response('simpleform.html',
                              {'core':core, 'additional':additional,
                               'project':project},
                              context_instance=RequestContext(request)
        )




def NewProject(request):
    if request.method == 'POST': 
        form = NewProjectForm(data=request.POST, user=request.user)
        if form.is_valid():
            new_project = form.save()
            return HttpResponseRedirect(new_project.get_absolute_url())
        else:
            return render_to_response('ProjectForm.html',
                              {'form':form},
                              context_instance=RequestContext(request))
            
    else:
        form = NewProjectForm(user=request.user)
    return render_to_response('ProjectForm.html',
                              {'form':form},
                              context_instance=RequestContext(request)
        )


def ReportUpload(request):
    pass


def uploadlist(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():

            newreport = Reports(report_path = request.FILES['report_path'])

            pdb.set_trace()
            newreport.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('pjtk2.views.uploadlist'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    reports = Reports.objects.all()
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
    
