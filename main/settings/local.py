from main.settings.base import *

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
         'ENGINE': 'django.contrib.gis.db.backends.postgis',
         'NAME': 'pjtk2',
         'USER': 'cottrillad',
         'PASSWORD': 'django123',
     }
}


#MIDDLEWARE = MIDDLEWARE + ['debug_toolbar.middleware.DebugToolbarMiddleware']
#
INSTALLED_APPS += (
    #'debug_toolbar',
    'django_extensions',
    #'werkzeug_debugger_runserver',

)

#INTERNAL_IPS = ('127.0.0.1', )   #added for debug toolbar


#def show_toolbar(request):
#    return True
#SHOW_TOOLBAR_CALLBACK = show_toolbar
