import warnings

from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.views.static import serve as serve_static
#from django.conf.urls.static import static
#from django.contrib.staticfiles.urls import staticfiles_urlpatterns

warnings.simplefilter('error', DeprecationWarning)

from pjtk2.views import project_list

admin.autodiscover()

urlpatterns = [

    url(r'^$', project_list, name='home'),
    url(r'^$', project_list, name='index'),

    url(r'^coregonusclupeaformis/admin/', admin.site.urls),

    url(r'^accounts/', include('simple_auth.urls')),
    url(r'^password_reset/',
        include('password_reset.urls')),

    url(r'^projects/', include('pjtk2.urls')),

    url(r'^tickets/', include('tickets.urls')),


    url(r'^static/(?P<path>.*)$',
            serve_static,
            {'document_root': settings.STATIC_ROOT}),

    url(r'^uploads/(?P<path>.*)$',
            serve_static,
            {'document_root': settings.MEDIA_ROOT}),

]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
