from main.settings.base import *

GEOS_LIBRARY_PATH = "c:/OSGeo4W/bin/geos_c.dll"
GDAL_LIBRARY_PATH = "C:/OSGeo4W/bin/gdal300.dll"


ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "pjtk2",
        "USER": "cottrillad",
        "PASSWORD": "django123",
    },
    "gldjango": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "gldjango",
        "USER": "cottrillad",
        "PASSWORD": "django123",
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
