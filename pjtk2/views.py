from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponseRedirect, HttpResponse
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory

from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator

from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.conf import settings


from pjtk2.models import Milestone, Project, Report, ProjectReports
from pjtk2.models import TL_ProjType, TL_Database
#from pjtk2.forms import MilestoneForm
from pjtk2.forms import ProjectForm, ApproveProjectsForm, DocumentForm, ReportsForm
from pjtk2.forms import AdditionalReportsForm, CoreReportsForm, AssignmentForm, ReportUploadForm

import os
import pdb
import mimetypes


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
    #reports = get_assignments(slug)
    #reports = project.get_assignment_dicts()

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
    #reports = get_assignments(slug)
    reports = project.get_assignment_dicts()

    if request.method=="POST":
        NewReport = request.POST.get('NewReport')
        if NewReport:
            NewReport = NewReport.title()
            #verify that this reporting requirement doesn't already exist
            # then add it to the reporting requirements
            try:
                Milestone.objects.get_or_create(label=NewReport)
            except Exception:
                pass
            #now redirect back to the update reports form for this project
            return HttpResponseRedirect(reverse('Reports', args=(project.slug,)))

        else:
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



def ReportUpload(request, slug):
    '''This view will render a formset with filefields for each of the
    reports associated with this project.'''

    #for development purposes, lets use a project that we know has
    #some reports associated with it.
    #slug = "zzz_zz13_zzz"
    project = Project.objects.get(slug=slug)

    #ReportFormSet = modelformset_factory(Report, ReportUploadForm, extra=0)
    #reports = project.get_reports()

    reports = get_assignments_with_paths(slug)
    ReportFormSet = formset_factory(ReportUploadForm, extra=0)

    formset = ReportFormSet(request.POST or None,  initial = reports)    
    
    if request.method == 'POST': 
        #formset = ReportFormSet(request.POST,  queryset = reports)
        formset = ReportFormSet(request.POST,  initial = reports)    
        if formset.is_valid(): 
            #do something
            return HttpResponseRedirect(project.get_absolute_url())
        #else:
        #formset = ReportFormSet(queryset = reports)
        #formset = ReportFormSet(initial = reports)
    return render_to_response('UploadReports.html', {
                'formset': formset,
                'project':project,
                },
                context_instance=RequestContext(request))



    



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




def serve_file(request, filename):
    '''from:http://stackoverflow.com/questions/2464888/downloading-a-csv-file-in-django?rq=1

    This function is my first attempt at a function used to
    serve/download files.  It works for basic text files, but seems to
    corrupt pdf and ppt files (maybe other binaries too).  It also
    should be updated to include some error trapping just incase the
    file doesn t actully exist.
    '''

    content_type = mimetypes.guess_type(filename)[0]

    #data = open(os.path.join(settings.MEDIA_ROOT,filename),'r').read()
    #resp = HttpResponse(data, mimetype='application/x-download')
    #resp = HttpResponse(data, mimetype=content_type)

    data = FileWrapper(file(os.path.join(settings.MEDIA_ROOT,filename),'rb'))
    resp = HttpResponse(data, mimetype=content_type)
    filename = os.path.split(filename)[-1]
    resp['Content-Disposition'] = 'attachment;filename=%s' % filename

    return resp








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
