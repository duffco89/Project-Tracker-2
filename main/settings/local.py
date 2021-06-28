from main.settings.base import *


ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "pjtk2",
        "USER": os.getenv("PGUSER"),
        "PASSWORD": os.getenv("PGPASS"),
    },
    "gldjango": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "gldjango",
        "USER": os.getenv("PGUSER"),
        "PASSWORD": os.getenv("PGPASS"),
    },
}


MIDDLEWARE = MIDDLEWARE + ["debug_toolbar.middleware.DebugToolbarMiddleware"]
#
INSTALLED_APPS += (
    "debug_toolbar",
    "django_extensions",
    #'werkzeug_debugger_runserver',
)

INTERNAL_IPS = ("127.0.0.1",)  # added for debug toolbar
