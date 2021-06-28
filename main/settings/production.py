from main.settings.base import *

GEOS_LIBRARY_PATH = "c:/OSGeo4W/bin/geos_c.dll"
GDAL_LIBRARY_PATH = "C:/OSGeo4W/bin/gdal300.dll"

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ["*"]
# ALLOWED_HOSTS = ['localhost', '127.0.0.1', '142.143.160.33']

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "pjtk2",
        "USER": os.getenv("PGUSER"),
        "PASSWORD": os.getenv("PGPASS"),,
        "HOST": "142.143.160.110",
    }
}
