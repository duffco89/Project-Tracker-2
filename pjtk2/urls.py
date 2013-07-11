from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, include, url


from haystack.forms import FacetedSearchForm
from haystack.query import SearchQuerySet
from haystack.views import FacetedSearchView

sqs = SearchQuerySet().facet('project_type').facet('lake').facet('funding')


urlpatterns = patterns('pjtk2.views',

    url(r'^search/$', FacetedSearchView(
       form_class=FacetedSearchForm, 
       searchqueryset=sqs), 
       name='haystack_search'),

    #(r'^search/', include('haystack.urls')),

    #CRUD Projects
    url(r'^projects/$', 'project_list', name='ProjectList'),
    url(r'^projects/approved$', 'approved_projects_list', 
        name='ApprovedProjectsList'),

    #project formset:
    url(r'^approveprojects/$', 'approveprojects', name='ApproveProjects'),
# url(r'^projectsbytype/(?P<projecttype>.+)$', 'projects_by_type', 
#       name='ProjectsByType'),
    
    url(r'^newproject/$', 'new_project', name='NewProject'),

    url((r'^copyproject/'
          '(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$'),
        'copy_project', name='CopyProject'),

    url((r'^editproject/'
          '(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$'),
        'edit_project', name='EditProject'),

    url((r'^projectdetail/'
          '(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$'),
        'project_detail', name='project_detail'),

    url(r'^myprojects/$', 'my_projects', name='MyProjects'),
        

    url((r'^sisterprojects/'
          '(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$'),
        'sisterprojects', name='SisterProjects'),

##     url(r'^projects/(?P<year>\d{4})/$',
##         'project_by_year', name='ProjectsByYear'),
## 

    #tagging/keywords                  
    url(r'^taggedprojects/(?P<tag>.+)/$', 'taggedprojects', 
        name='TaggedProjects'),

    
# Reports and milestones
    url(r'^reports/(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$',
        'report_milestones', name='Reports'),

#    url(r'^reportformset/', 'report_formset', name='ReportFormSet'),

#    url((r'^updateassignments/'
#            '(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$'),
#        'update_assignments', name='UpdateAssignments'),


#url(r'^(?P<slug>[A-Z]{3}_[A-Z]{2}\d{2}_([A-Z]|\d){3})/$',
#       'project_milestones', name='ProjectMilestones'),


    url((r'^reportupload/'
        '(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$'),
        'report_upload', name='ReportUpload'),
    
    url(r'^uploadlist/$', 'uploadlist', name='UploadList'),

    #this function is used to download reports and files from project pages
    url(r'^serve_file/(?P<filename>.+)/$', 'serve_file', name='serve_file'),    


#bookmarking
    url((r'^bookmarkproject/'
          '(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$'),
          'bookmark_project', name='Bookmark_Project'),

    url((r'^unbookmarkproject/'
          '(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$'),
          'unbookmark_project', name='Unbookmark_Project'),

)


