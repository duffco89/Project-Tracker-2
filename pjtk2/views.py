from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.context_processors import csrf
from django.views.generic import ListView
from django.core.urlresolvers import reverse


from pjtk2.models import Milestone, Project
#from pjtk2.forms import MilestoneForm
from pjtk2.forms import AdditionalReportsForm, CoreReportsForm, NewProjectForm



class ProjectList(ListView):
    queryset = Project.objects.all()
    template_name = "ProjectList.html"
    
project_list = ProjectList.as_view()


def ReportMilestones(request):
    #reports = MilestoneForm()
    core =  CoreReportsForm()
    additional = AdditionalReportsForm()

    return render_to_response('simpleform.html',
                              {'core':core, 'additional':additional},
                              context_instance=RequestContext(request)
        )

g
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
