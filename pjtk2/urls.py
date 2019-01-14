from django.contrib.auth.decorators import login_required

from django.conf.urls import include, url


from haystack.forms import FacetedSearchForm
from haystack.query import SearchQuerySet
from haystack.views import FacetedSearchView

sqs = (SearchQuerySet().order_by('-year').facet('project_type').
       facet('lake').facet('funding'))

from pjtk2.views import (
    about_view,
    report_desc_view,
    project_list, user_project_list, project_list_q, approved_projects_list,
    approveprojects, approve_project,
    cancel_project, uncancel_project, signoff_project, reopen_project,
    new_project, copy_project, edit_project, project_detail, my_projects,
    employee_projects, sisterprojects,
    taggedprojects, project_tag_list,
    find_projects_roi_view, report_milestones,
    delete_report, report_upload,
    associated_file_upload, delete_associated_file,
    serve_file, bookmark_project, unbookmark_project,
    project_add_image, project_sort_images, project_images,
    edit_image, delete_image_file
)


PRJ_CD_REGEX = r'(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$'

urlpatterns = [

    url(r'^api/', include('pjtk2.api.urls', namespace='api')),

    url(r'^search/$', FacetedSearchView(
        form_class=FacetedSearchForm,
        searchqueryset=sqs),
        name='haystack_search'),

    url(r'^about/$', about_view, name = 'about_view'),
    url(r'^report_descriptions/$',
        report_desc_view,
        name = 'report_desc_view'),

    #CRUD Projects
    url(r'^projects/$',
        project_list,
        name='ProjectList'),

    url(r'^projects/(?P<username>.+)/$',
        user_project_list,
        name='user_project_list'),

    url(r'^projects/?q=$',
        project_list_q,
        name='ProjectList_q'),

    url(r'^projects/approved$',
        approved_projects_list,
        name='ApprovedProjectsList'),

    #project formset:
    url(r'^approveprojects/$', approveprojects, name='ApproveProjects'),
# url(r'^projectsbytype/(?P<projecttype>.+)$', 'projects_by_type',
#       name='ProjectsByType'),


    url((r'^approve_project/' + PRJ_CD_REGEX),
        approve_project,
        name='approve_project'),

    #url((r'^unapprove_project/'
    #      PRJ_CD_REGEX),
    #    'unapprove_project', name='unapprove_project'),

    url((r'^cancel_project/' + PRJ_CD_REGEX),
        cancel_project,
        name='cancel_project'),

    url((r'^uncancel_project/' + PRJ_CD_REGEX),
        uncancel_project,
        name='uncancel_project'),

    url((r'^signoff_project/' + PRJ_CD_REGEX),
        signoff_project,
        name='signoff_project'),


    url((r'^reopen_project/' + PRJ_CD_REGEX),
        reopen_project,
        name='reopen_project'),

    url(r'^newproject/$',
        new_project,
        name='NewProject'),

    url((r'^copyproject/' + PRJ_CD_REGEX),
        copy_project, name='CopyProject'),

    url((r'^editproject/' + PRJ_CD_REGEX),
        edit_project, name='EditProject'),

    url((r'^projectdetail/' + PRJ_CD_REGEX),
        project_detail, name='project_detail'),

    url(r'^myprojects/$',
        my_projects, name='MyProjects'),


    url(r'^employeeprojects/(?P<employee_name>.+)$',
        employee_projects,
        name='EmployeeProjects'),

    url((r'^sisterprojects/' + PRJ_CD_REGEX),
        sisterprojects, name='SisterProjects'),


    # images
    url((r'project/add_image/' + PRJ_CD_REGEX), project_add_image,
         name='project_add_image'),

    url((r'project/images/' + PRJ_CD_REGEX), project_images,
         name='project_images'),

    url((r'project/sort_images/' + PRJ_CD_REGEX), project_sort_images,
         name='project_sort_images'),

    # images
    url((r'project/edit_image/(?P<pk>\d+)'),
        edit_image,
         name='project_edit_image'),

   url((r'^project/delete_image/'
        '(?P<pk>\\d+)/$'),
        view=delete_image_file,
        name='delete_image_file'),


    #tagging/keywords
    url(r'^taggedprojects/(?P<tag>.+)/$',
        taggedprojects,
        name='TaggedProjects'),

    url(r'^tags/$',
        project_tag_list,
        name='project_tag_list'),


    #projects by region of interest:
    url(r'^projects_roi/$',
        find_projects_roi_view,
        name='find_projects_roi'),

    #projects by management unit:
    #url(
    #    regex=r'^projects_managment_unit/(?P<mu>[-A-Za-z0-9]+)$',
    #    view=find_projects_mu_view,
    #    name='find_projects_mu'
    #    ),



# Reports and milestones
    url(r'^reports/(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$',
        report_milestones, name='Reports'),

#    url(r'^reportformset/', 'report_formset', name='ReportFormSet'),

#    url((r'^updateassignments/'
#            PRJ_CD_REGEX),
#        'update_assignments', name='UpdateAssignments'),


#url(r'^(?P<slug>[A-Z]{3}_[A-Z]{2}\d{2}_([A-Z]|\d){3})/$',
#       'project_milestones', name='ProjectMilestones'),


   url((r'^delete_report/'
        r'(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/'
        r'(?P<pk>\d+)/$'),
        view=delete_report,
        name='delete_report'),


    url((r'^reportupload/' + PRJ_CD_REGEX),
        report_upload,
        name='ReportUpload'),

    url((r'^associatedfileupload/' + PRJ_CD_REGEX),
        associated_file_upload,
        name='associated_file_upload'),

   url((r'^delete_associated_file/'
        r'(?P<id>\d+)/$'),
        view=delete_associated_file,
        name='delete_associated_file'),

    #url(r'^uploadlist/$', 'uploadlist', name='UploadList'),

    #this function is used to download reports and files from project pages
    url(r'^serve_file/(?P<filename>.+)/$',
        serve_file,
        name='serve_file'),


#bookmarking
    url((r'^bookmarkproject/' + PRJ_CD_REGEX),
        bookmark_project,
        name='Bookmark_Project'),

    url((r'^unbookmarkproject/' + PRJ_CD_REGEX),
        unbookmark_project,
        name='Unbookmark_Project'),

]
