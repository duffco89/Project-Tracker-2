from django.conf.urls import patterns, include, url

#import pjtk2.views


urlpatterns = patterns('pjtk2.views',

    #CRUD Projects
    url(r'^projects/$', 'project_list', name='ProjectList'),
    url(r'^projects/approved$', 'approved_projects_list', name='ApprovedProjectsList'),
    #project formset:
    url(r'^projectsformset/$', 'project_formset', name='ProjectFormSet'),
    
    url(r'^newproject/$', 'new_project', name='NewProject'),
    
    url(r'^copyproject/(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$',
        'copy_project', name='CopyProject'),
        
    url(r'^editproject/(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$',
        'edit_project', name='EditProject'),

    url(r'^projectdetail/(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$',
        'ProjectDetail', name='ProjectDetail'),


# Reports and milestones    
    url(r'^reports/(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$',
        'report_milestones', name='Reports'),

#    url(r'^reportformset/', 'report_formset', name='ReportFormSet'),

        
    
#url(r'^(?P<slug>[A-Z]{3}_[A-Z]{2}\d{2}_([A-Z]|\d){3})/$', 
#       'project_milestones', name='ProjectMilestones'),


    
    url(r'^reportupload/$', 'ReportUpload', name='ReportUpload'),
    url(r'^uploadlist/$', 'uploadlist', name='UploadList'),

    # some silly examples
    url(r'^crispy/$', 'crispy', name='CrispyForm'),
    url(r'^crispy2/$', 'crispy2', name='CrispyForm2'),
)
