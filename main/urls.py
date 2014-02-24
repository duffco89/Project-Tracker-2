import warnings

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
#from django.conf.urls.static import static
#from django.contrib.staticfiles.urls import staticfiles_urlpatterns

warnings.simplefilter('error', DeprecationWarning)

from pjtk2.views import project_list

admin.autodiscover()

urlpatterns = patterns('',
                       
                       url(r'^$', project_list, name='home'),
                       url(r'^$', project_list, name='index'),
                       
                       url(r'^coregonusclupeaformis/admin/',
                           include(admin.site.urls), name='admin'),
                       
                       url(r'^accounts/', include('simple_auth.urls')),
                       url(r'^password_reset/',
                           include('password_reset.urls')),
                       
                       url(r'^projects/', include('pjtk2.urls')),

                       url(r'^tickets/', include('tickets.urls')),
)

#urlpatterns += staticfiles_urlpatterns()
urlpatterns += patterns('',
                        (r'^static/(?P<path>.*)$',
                         'django.views.static.serve',
                         {'document_root': settings.STATIC_ROOT}),)
