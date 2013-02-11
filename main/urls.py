from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
     url(r'^admin/', include(admin.site.urls)),
     url(r'^test/', include('pjtk2.urls')),

)

urlpatterns += patterns('',
        (r'^static_root/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'static'})
        )
