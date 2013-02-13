from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.context_processors import csrf
from django.views.generic import ListView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from pjtk2.models import Milestone, Project
#from pjtk2.forms import MilestoneForm
from pjtk2.forms import AdditionalReportsForm, CoreReportsForm, NewProjectForm

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



##  #from http://www.allbuttonspressed.com/projects/django-filetransfers
##  from filetransfers.api import prepare_upload
##  
##  def upload_handler(request):
##      view_url = reverse('upload.views.upload_handler')
##      if request.method == 'POST':
##          form = UploadForm(request.POST, request.FILES)
##          form.save()
##          return HttpResponseRedirect(view_url)
##  
##      upload_url, upload_data = prepare_upload(request, view_url)
##      form = UploadForm()
##      return direct_to_template(request, 'upload/upload.html',
##          {'form': form, 'upload_url': upload_url, 'upload_data': upload_data})
