from django.conf.urls import patterns, include, url

#import pjtk2.views


urlpatterns = patterns('pjtk2.views',
    url(r'^reports/$', 'ReportMilestones', name='Reports'),
    url(r'^newproject/$', 'NewProject', name='NewProject'),
    url(r'^projects/$', 'project_list', name='ProjectList'),
    url(r'^viewreports/(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$',
        'ViewReports', name='ViewReports'),

    url(r'^copyproject/(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$',
        'copy_project', name='CopyProject'),
        
    url(r'^editproject/(?P<slug>[A-Za-z]{3}_[A-Za-z]{2}\d{2}_([A-Za-z]|\d){3})/$',
        'edit_project', name='EditProject'),

        
    url(r'^(?P<slug>[A-Z]{3}_[A-Z]{2}\d{2}_([A-Z]|\d){3})/$', 'project_milestones', name='ProjectMilestones'),
    
    url(r'^reportupload/$', 'ReportUpload', name='ReportUpload'),
    url(r'^uploadlist/$', 'uploadlist', name='UploadList'),
    url(r'^crispy/$', 'crispy', name='CrispyForm'),
    url(r'^crispy2/$', 'crispy2', name='CrispyForm2'),
)
