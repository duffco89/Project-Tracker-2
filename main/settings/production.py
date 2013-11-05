from main.settings.base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

#ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '142.143.160.33']

#username and password: cottrillad, django
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '%s/db/pjtk2.db' % root(),
    }
}


