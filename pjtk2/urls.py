from django.conf.urls import patterns, include, url

from pjtk2.views import ReportMilestones


urlpatterns = patterns('',
    url(r'^reports/$', ReportMilestones),     
)
