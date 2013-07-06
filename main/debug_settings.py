#python manage.py runserver_plus --settings=main.debug_settings


from settings import *

DEBUG = True
INTERNAL_IPS = ('127.0.0.1', )   #added for debug toolbar and werkzueg
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}
