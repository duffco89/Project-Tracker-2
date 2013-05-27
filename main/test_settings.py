# usage: python manage.py test pjtk2 --settings=main.test_settings
# flake8: noqa
"""Settings to be used for running tests."""
import os

from main.settings import *


INSTALLED_APPS += ('django_nose',)
#INSTALLED_APPS.append('django_jasmine')

## DATABASES = {
##     "default": {
##         "ENGINE": "django.db.backends.sqlite3",
##         "NAME": ":memory:",
##     }
## }

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}


#EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
SOUTH_TESTS_MIGRATE = False

TEST_RUNNER = 'main.testrunner.NoseCoverageTestRunner'
COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'admin$', 'django_extensions',
]
COVERAGE_MODULE_EXCLUDES += THIRDPARTY_APPS + DJANGO_APPS
COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(__file__, '../../coverage')
