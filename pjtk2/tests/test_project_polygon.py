'''=============================================================
c:/1work/Python/djcode/pjtk2/pjtk2/tests/test_project_polygon.py
Created: 24 Nov 2017 14:11:25

DESCRIPTION:

This scripts contains a number of pytest fixtures and unit tests to
verify that the functions associated with project polygon work as
expected.

A. Cottrill
=============================================================

'''

from django.contrib.gis.geos import GEOSGeometry

from pjtk2.models import Project, SamplePoint, ProjectPolygon
#from pjtk2.spatial_utils import *
from pjtk2.tests.factories import *

import pytest


def assign_pts_to_project(project, points):
    """
    """
    for pt in points:
        SamplePointFactory.create(project=project,
                                    geom=GEOSGeometry(pt,srid=4326))


def delete_points(project):
    """
    """
    points = project.samplepoint_set.all()
    for pt in points:
        pt.delete()

@pytest.fixture
def project(scope='session'):
    """create a project that will be used for our tests
    """
    prj_cd = 'LHA_IA13_DIS'
    project = ProjectFactory.create(prj_cd=prj_cd)

    return(project)


@pytest.mark.django_db
def test_project_polygon_none(project):
    """If we have a project without any spatial points, we should not be
    able to created a projectpolygon.
    """

    project.update_convex_hull()

    #assert hasattr(project, 'convex_hull') is False
    assert project.convex_hull.geom is None

@pytest.mark.django_db
def test_project_new_polygon(project):
    """if we have a project with at least three sample points that form a
    valid polygon, we should be able to create a project polygon
    object from those points and save it.

    """
    pts = ['POINT(-82.0416679351682 43.9583319806175)',
           'POINT(-82.1249999941107 44.0416640136496)',
           'POINT(-81.9583320623296 44.0416640159647)']

    assign_pts_to_project(project, pts)

    project.update_convex_hull()

    assert hasattr(project, 'convex_hull') is True


@pytest.mark.django_db
def test_project_polygon_point(project):
    """If we have a project with just one spatial point, we should not
    be able to create a projectpolygon as a single point does not
    form a polygon.
    """


    foo = project.get_sample_points()
    print('foo={}'.format(foo))

    pts = ['POINT(-82.0416679351682 43.9583319806175)',]
    assign_pts_to_project(project, pts)

    project.update_convex_hull()

    assert project.convex_hull.geom is None



@pytest.mark.django_db
def test_project_polygon_line(project):
    """if we have a project with two sample points, we should not
    be able to create a projectpolygon as a single point does not
    form a polygon.
    """

    pts = ['POINT(-82.0416679351682 43.9583319806175)',
           'POINT(-81.9583320623296 44.0416640159647)']

    assign_pts_to_project(project, pts)

    project.update_convex_hull()

    assert project.convex_hull.geom is None


@pytest.mark.django_db
def test_project_invalid_polygon(project):
    """if we have a project with three points sample points, two of which
    are the same.  We can create a line, but not a polygon.

    """

    pts = ['POINT(-82.0416679351682 43.9583319806175)',
           'POINT(-82.0416679351682 43.9583319806175)',
           'POINT(-81.9583320623296 44.0416640159647)']

    assign_pts_to_project(project, pts)
    project.update_convex_hull()

    assert project.convex_hull.geom is None


@pytest.mark.django_db
def test_project_polygon_changed_to_none(project):
    """
    """

    pts = ['POINT(-82.0416679351682 43.9583319806175)',
           'POINT(-82.1249999941107 44.0416640136496)',
           'POINT(-81.9583320623296 44.0416640159647)']

    assign_pts_to_project(project, pts)

    project.update_convex_hull()
    original = project.convex_hull
    assert original is not None

    delete_points(project)
    assert len(project.get_sample_points()) is 0
    project.update_convex_hull()


    proj = Project.objects.get(id=project.id)
    assert hasattr(proj, 'convex_hull') is False



@pytest.mark.django_db
def test_project_polygon_changed(project):
    """If the points sampled in a proejct change, the convex hull could
    change too (will change if the change occurs on the periphery of
    the sampling region.)

    """

    pts = ['POINT(-82.0416679351682 43.9583319806175)',
           'POINT(-82.1249999941107 44.0416640136496)',
           'POINT(-81.9583320623296 44.0416640159647)']

    assign_pts_to_project(project, pts)

    project.update_convex_hull()
    assert project.convex_hull is not None
    original =  project.convex_hull.geom
    print('original={}'.format(original))

    delete_points(project)

    #add another point
    pts = ['POINT(-82.081126628131 44.000970817096)',
           'POINT(-82.0456637754061 44.0649121962459)',
           'POINT(-82.024922507764 44.0171801372301)',
           'POINT(-82.0017671634393 44.0513359855003)']
    assign_pts_to_project(project, pts)
    project.update_convex_hull()

    updated = project.convex_hull
    assert updated is not None
    print('updated.geom={}'.format(str(updated.geom)))
    assert updated.geom != original
