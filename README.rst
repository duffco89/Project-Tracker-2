=====
Project Tracker II
=====

pjtk2 is a Django application that provides an interface and API for
reports and milestones associated with Great Lakes Fisheries
Assessment Porgrams. It is built as an installable application that
can be added to other projects as needed.

More detailed documentation is in the "docs" directory.

Quick start
-----------

0. > pip install pjtk2.zip

1. Add django-taggid, pjtk2, and common and to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,        
        "taggit",
        "common",
        "pjtk2",
    ]g

2. Include the pjtk2 URLconf in your project urls.py like this::

     path("pjtk2/", include(pjtk2_urls, namespace="pjtk2")),
     
3. Run `python manage.py migrate` to create the pjtk2 models.

4. Visit http://127.0.0.1:8000/pjtk2 


Updating the Application
------------------------


Rebuilding the App.
------------------------

PJTK2 was built as a standard applicaiton can be rebuild for
distrubition following the instructions found here:

https://docs.djangoproject.com/en/2.2/intro/reusable-apps/

With the pjtk2 virtualenv active, and from within the
~/django_pjtk2 directory, simply run:

> python setup.py sdist

The package will be placed in the ~/dist folder.  To install the
application run the command:

> pip install pjtk2.zip

To update an existing application issue the command:

> pip install --upgrade pjtk2.zip


Running the tests
------------------------

pjtk2 contains a number of unit tests that verify that the
application works as expected and that any regregressions are caught
early. The package uses pytest to run all of the tests, which can be
run by issuing the command:

> pytest

After the tests have completed, coverage reports can be found here:

~/htmlcov

NOTE: you may have to modify the settings GEOS_LIBRARY_PATH and
GDAL_LIBRARY_PATH to point to the locations on your computer for the
tests (and application) to run.
