from django.conf.urls import patterns, include, url

from pjtk2.views import ReportMilestones, NewProject, project_list, project_milestones


urlpatterns = patterns('',
    url(r'^reports/$', ReportMilestones),
    url(r'^newproject/$', NewProject, name='NewProject'),
    url(r'^projects/$', project_list, name='ProjectList'),     
                     
    url(r'^(?P<slug>[A-Z]{3}_[A-Z]{2}\d{2}_([A-Z]|\d){3})/$', project_milestones, name='ProjectMilestones'),         
)
