
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.context_processors import csrf
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.core.servers.basehttp import FileWrapper
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.decorators import method_decorator


from pjtk2.filters import ProjectFilter
from pjtk2.models import Milestone, Project, Report, ProjectReports
from pjtk2.models import TL_ProjType, TL_Database, Bookmark, ProjectSisters, Family
#from pjtk2.forms import MilestoneForm
from pjtk2.forms import ProjectForm, ApproveProjectsForm, DocumentForm, ReportsForm
from pjtk2.forms import SisterProjectsForm
#from pjtk2.forms import AdditionalReportsForm, CoreReportsForm, AssignmentForm

from pjtk2.forms import  ReportUploadForm,  ReportUploadFormSet

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


def get_assignments_with_paths(slug, Core=True):
    '''function that will return a list of dictionaries for each of the
    reporting requirements.  each dictionary will indicate what the
    report is required, whether or not it has been requested for this
    project, and if it is available, a path to the associated
    report.'''

    project = Project.objects.get(slug=slug)

    if Core:
        assignments = project.get_core_assignments()
    else:
        assignments = project.get_custom_assignments()

    assign_dicts = []
    for assignment in assignments:
        try:
            filepath = Report.objects.get(projectreport=assignment, current=True)
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


class ListFilteredMixin(object):
    """ Mixin that adds support for django-filter
    from: https://github.com/rasca/django-enhanced-cbv/blob/master/enhanced_cbv/views/list.py
"""
    filter_set = None
 
    def get_filter_set(self):
        if self.filter_set:
            return self.filter_set
        else:
            raise ImproperlyConfigured(
                "ListFilterMixin requires either a definition of "
                "'filter_set' or an implementation of 'get_filter()'")

    def get_filter_set_kwargs(self):
        """ Returns the keyword arguments for instanciating the filterset."""
        return {
            'data': self.request.GET,
            'queryset': self.get_base_queryset(),
        }

    def get_base_queryset(self):
        """ We can decided to either alter the queryset before or
        after applying the FilterSet """

        return super(ListFilteredMixin, self).get_queryset()

    def get_constructed_filter(self):
        # We need to store the instantiated FilterSet cause we use it in
        # get_queryset and in get_context_data
        if getattr(self, 'constructed_filter', None):
            return self.constructed_filter
        else:
            f = self.get_filter_set()(**self.get_filter_set_kwargs())
            self.constructed_filter = f
            return f

    def get_queryset(self):
        return self.get_constructed_filter().qs

    def get_context_data(self, **kwargs):
        kwargs.update({'filter': self.get_constructed_filter()})
        return super(ListFilteredMixin, self).get_context_data(**kwargs)


class ProjectList(ListFilteredMixin, ListView):
    """ A list view that can be filtered by django-filter """
    
    #(maybe??) modified to accept tag argument 

    filter_set = ProjectFilter

    if self.tag:
        queryset = Project.objects.filter(tags__name__int=tag)
    else:    
        queryset = Project.objects.all()

    template_name = "ProjectList.html"

    def __init__(self, *args, **kwargs):
        self.tag = kwargs.pop('tag', None) 
        return super(ProjectList, self).__init__(*args, **kwargs)


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        #tag = kwargs.pop('tag', None)
        return super(ProjectList, self).dispatch(*args, **kwargs)

project_list = ProjectList.as_view()

#subset of projects tagged with tag:
taggedprojects = ProjectList.as_view(tag=tag)










#class ProjectList(ListView):
#    queryset = Project.objects.all()
#    template_name = "ProjectList.html"

#    @method_decorator(login_required)
#    def dispatch(self, *args, **kwargs):
#        return super(ProjectList, self).dispatch(*args, **kwargs)

#project_list = ProjectList.as_view()


# class ProjectByProjectType(ListView):
#     projecttype = self.kwarg["projecttype"]
#     queryset = Project.objects.filter(ProjectType=projecttype)
#     template_name = "ProjectList.html"
# 
#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super(ProjectList, self).dispatch(*args, **kwargs)
# 
# project_by_type = ProjectByProjectType.as_view()




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

    Core = get_assignments_with_paths(slug)
    Custom = get_assignments_with_paths(slug, Core=False)

    user = User.objects.get(username__exact=request.user)
    edit = canEdit(user, project)
    manager = is_manager(user)

    return render_to_response('projectdetail.html',
                              {'Core':Core,
                               'Custom':Custom,
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
            Core =  ReportsForm(request.POST, project=project, reports=reports)
            Custom = ReportsForm(request.POST, project=project, reports = reports,
                                 Core=False)

            if Core.is_valid() and Custom.is_valid():
                Core.save()
                Custom.save()

                return HttpResponseRedirect(project.get_absolute_url())
    else:
        Core =  ReportsForm(project=project, reports = reports)
        Custom =  ReportsForm(project=project, reports = reports, Core=False)


    return render_to_response('reportform.html',
                              {'Core':Core,
                               'Custom':Custom,
                               'project':project
                               },
                              context_instance=RequestContext(request)
        )


@login_required
def ReportUpload(request, slug):
    '''This view will render a formset with filefields for each of the
    reports associated with this project.  It used a custom formset
    that has been extended to accept a user and a project - these are
    needed to insert Reports.'''

    project = Project.objects.get(slug=slug)

    #get the core and custom reports associated with this project
    reports = get_assignments_with_paths(slug)
    Custom =  get_assignments_with_paths(slug, Core=False)
    if Custom:
        [reports.append(x) for x in Custom]
    
    ReportFormSet = formset_factory(ReportUploadForm, 
                                    formset=ReportUploadFormSet, extra=0)
    
    if request.method == 'POST': 
        formset = ReportFormSet(request.POST,  request.FILES, 
                                initial = reports, 
                                project = project,
                                user = request.user)    
        if formset.is_valid(): 
            for form in formset:
                form.save()
                #form.save_m2m()
            return HttpResponseRedirect(project.get_absolute_url())
    else:
        formset = ReportFormSet(initial = reports)
    return render_to_response('UploadReports.html', {
                'formset': formset,
                'project':project,
                },
                context_instance=RequestContext(request))



    


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
    response = HttpResponse(data, mimetype=content_type)
    filename = os.path.split(filename)[-1]
    response['Content-Disposition'] = 'attachment;filename=%s' % filename

    return response





@login_required
def my_projects(request):
    #TODO - write test to verify this works as expected.
    bookmarks = Bookmark.objects.filter(user__pk=request.user.id)

    myprojects = Project.objects.filter(Owner__username=request.user.username) 
    
    complete = myprojects.filter(SignOff=True)
    approved = myprojects.filter(Approved=True).filter(SignOff=False)
    submitted = myprojects.filter(Approved=False)
    
    template_name = "my_projects.html"

    return render_to_response(template_name,
                              { 'bookmarks':bookmarks,
                                'complete':complete,
                                'approved':approved,
                                'submitted':submitted                                                                },
                              context_instance=RequestContext(request))

    

#=====================
#Bookmark views
@login_required
def bookmark_project(request, slug):
    '''Modified from Practical Django Projects - pg 189.'''
    #TODO - write test to verify this works as expected.
    project = get_object_or_404(Project, slug=slug)
    try:
        Bookmark.objects.get(user__pk=request.user.id,
                             project__slug=project.slug)
    except Bookmark.DoesNotExist:
        bookmark = Bookmark.objects.create(user=request.user,
                                           project=project)
    return HttpResponseRedirect(project.get_absolute_url())


@login_required    
def unbookmark_project(request, slug):
    #TODO - write test to verify this works as expected.
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        Bookmark.objects.filter(user__pk=request.user.id,
                                project__pk=project.id).delete()
        return HttpResponseRedirect(project.get_absolute_url())
    else:
        return render_to_response('confirm_bookmark_delete.html',
                                  { 'project': project },
                                  context_instance=RequestContext(request))


#=====================

def get_sisters_dict(slug):
    '''given a slug, return a list of dictionaries of projects that
    are (or could be) sisters to the given project.  Values returned
    by this function are used to populate the sister project formset'''
    
    project = get_object_or_404(Project, slug=slug)
    initial=[]
    
    family = project.get_family()
    sisters = project.get_sisters()
    candidates = project.get_sister_candidates()
        
    if sisters:
        for proj in sisters:
            initial.append(dict(sister=True, PRJ_CD = proj.PRJ_CD, 
                                slug=proj.slug, PRJ_NM = proj.PRJ_NM, 
                                PRJ_LDR = proj.PRJ_LDR))
    if candidates:
        for proj in candidates:
            initial.append(dict(sister=False, PRJ_CD = proj.PRJ_CD, 
                                slug=proj.slug, PRJ_NM = proj.PRJ_NM, 
                                PRJ_LDR = proj.PRJ_LDR))
    return initial


def sisterprojects(request, slug):
    '''render a form that can be used to create groupings of sister
    projects.  Only approved projects in the same year, and of the
    same project type will be presented.  existing sister projects
    will be checked off.  When the form is submitted the sibling
    relationships will be updated according to the values in the
    sister of each returned form.'''

    project = get_object_or_404(Project, slug=slug)
    initial = get_sisters_dict(slug)
    empty = True if len(initial)==0 else False
        
    SisterFormSet = formset_factory(SisterProjectsForm, extra=0)

    if request.method == 'POST': 
        formset = SisterFormSet(request.POST, request.FILES, initial=initial)
        if formset.is_valid():
            #see if any checkboxes have changed
            cleandata = [x.cleaned_data['sister'] for x in formset]
            init = [x.initial['sister'] for x in formset]            
            #if cleandata==init, there is nothing to do
            if cleandata != init:                    
                #if all cleandata==False then remove this project from this family
                if all(x==False for x in cleandata):
                    project.disown()
                else:
                    for form in formset:
                        form.save(parentslug=slug)
            return HttpResponseRedirect(project.get_absolute_url())
    else:
        formset = SisterFormSet(initial=initial)
    return render_to_response('SisterProjects.html', {
                'formset': formset,
                'project':project,
                'empty':empty
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
