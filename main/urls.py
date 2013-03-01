from django.conf.urls import patterns, include, url

from django.conf import settings
from django.conf.urls.static import static

#from django.views.generic.simple import direct_to_template


from pjtk2.views import HomePageView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                
     url(r'^$', HomePageView.as_view(), name='home'),                       
     #url(r'^$', direct_to_template, {'template': 'index.html'},name='home'),
     url(r'^admin/', include(admin.site.urls), name='admin'),
     url(r'^test/', include('pjtk2.urls')),
     )  #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += patterns('',
        (r'^static_root/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'static'}),
            )
