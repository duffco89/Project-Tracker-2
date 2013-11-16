from main.settings.base import *


#username and password: cottrillad, django
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': '%s/db/pjtk2.db' % root(),
#    }
#}


DATABASES = {
    'default': {
         'ENGINE': 'django.contrib.gis.db.backends.postgis',
         'NAME': 'pjtk2',
         'USER': 'adam',
         'PASSWORD': 'django',
     }
}



MIDDLEWARE_CLASSES += (   
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS += (
    'debug_toolbar',
    'django_extensions',
    'werkzeug_debugger_runserver',
)

INTERNAL_IPS = ('127.0.0.1', )   #added for debug toolbar
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}


def show_toolbar(request):
    return True
SHOW_TOOLBAR_CALLBACK = show_toolbar
