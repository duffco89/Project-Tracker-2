from django.conf.urls import patterns, include, url

from pjtk2.views import ReportMilestones, NewProject, project_list


urlpatterns = patterns('',
    url(r'^reports/$', ReportMilestones),
    url(r'^newproject/$', NewProject, name='NewProject'),
    url(r'^projects/$', project_list, name='ProjectList'),     
)
