from main.settings.base import *

#username and password: cottrillad, django
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '%s/db/pjtk2.db' % root(),
    }
}

