from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

import warnings
warnings.simplefilter('error', DeprecationWarning)

from pjtk2.views import HomePageView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                
     url(r'^$', HomePageView.as_view(), name='home'),                       
     url(r'^admin/', include(admin.site.urls), name='admin'),
     url(r'^test/', include('pjtk2.urls')),
     )  #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




urlpatterns += patterns('',
        (r'^static_root/(?P<path>.*)$', 'django.views.static.serve',
              {'document_root': 'static'}),

        url(r'^accounts/login/$', 'django.contrib.auth.views.login', 
            {'template_name':'auth/login.html'},name='login'),
        url(r'^accounts/logout/$', 'pjtk2.views.logout_view',name='logout'), 

            )
