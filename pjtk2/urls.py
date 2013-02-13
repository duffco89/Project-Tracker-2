from django.conf.urls import patterns, include, url

#import pjtk2.views


urlpatterns = patterns('pjtk2.views',
    url(r'^reports/$', 'ReportMilestones', name='Reports'),
    url(r'^newproject/$', 'NewProject', name='NewProject'),
    url(r'^projects/$', 'project_list', name='ProjectList'),
    url(r'^viewreports/(?P<slug>[A-Z]{3}_[A-Z]{2}\d{2}_([A-Z]|\d){3})/$',
        'ViewReports', name='ViewReports'),

    url(r'^(?P<slug>[A-Z]{3}_[A-Z]{2}\d{2}_([A-Z]|\d){3})/$', 'project_milestones', name='ProjectMilestones'),
    
    url(r'^reportupload/$', 'ReportUpload', name='ReportUpload'),
)
