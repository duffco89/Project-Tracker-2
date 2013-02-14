from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.context_processors import csrf
from django.views.generic import ListView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from pjtk2.models import Milestone, Project, Reports
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



def ViewReports(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method=="POST":
        core =  CoreReportsForm(request.POST, slug)
        #pdb.set_trace()
        if core.is_valid():
            #form.save()
            return HttpResponseRedirect(reverse('ProjectList'))
    else:
        core =  CoreReportsForm(slug)
    #reports = MilestoneForm()

    #additional = AdditionalReportsForm()

    return render_to_response('simpleform.html',
                              {'core':core, 
                               #'additional':additional,
                               'project':project
                               },
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

    if request.method == 'POST': # If the form has been submitted...
        form = NewProjectForm(request.POST) # A form bound to the POST data
        if form.is_valid():
           project = form.cleaned_data()
           project.save()
           pk = project.pk
        return HttpResponseRedirect()
    else:
        form = NewProjectForm() # An unbound form
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

    
