import warnings

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
#from django.conf.urls.static import static
#from django.contrib.staticfiles.urls import staticfiles_urlpatterns


warnings.simplefilter('error', DeprecationWarning)

from pjtk2.views import HomePageView

# Uncomment the next two lines to enable the admin:

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', HomePageView.as_view(), name='home'),
                       url(r'^coregonusclupeaformis/admin/',
                           include(admin.site.urls), name='admin'),
                       url(r'^test/', include('pjtk2.urls')),)

# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#login/logout (eventually replace)
urlpatterns += patterns('',
                        url(r'^accounts/login/$',
                            'django.contrib.auth.views.login',
                            {'template_name': 'auth/login.html'},
                            name='login'),
                        url(r'^accounts/logout/$',
                            'pjtk2.views.logout_view',
                            name='logout'),)

#urlpatterns += staticfiles_urlpatterns()
urlpatterns += patterns('',
                        (r'^static/(?P<path>.*)$',
                         'django.views.static.serve',
                         {'document_root': settings.STATIC_ROOT}),)
