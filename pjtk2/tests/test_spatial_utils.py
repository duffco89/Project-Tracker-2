'''=============================================================
c:/1work/Python/djcode/pjtk2/pjtk2/tests/test_spatial_utils.py
Created: 10 Jul 2014 08:51:49


DESCRIPTION:

This scripts contains a number of pytest fixtures and unit tests to
verify that the functions associated with spatial analysis work as
eexpected.

A. Cottrill
=============================================================

'''

from django.contrib.gis.geos import GEOSGeometry

from pjtk2.spatial_utils import Project, SamplePoint
from pjtk2.spatial_utils import *
from pjtk2.tests.factories import *

import pytest

@pytest.fixture
def roi():
    """a region of interest that can be used in all of our tests.  Uses
    corrdinates of grid 2826, a 5-minute grid in the middle of Lake
    Huron located at the intersection of 44 degrees latitude and 82
    degrees longitude..
    """
    grid = ('MULTIPOLYGON(((-82.000000033378 43.9999999705306,' +
            '-82.0833359084557 43.9999999705305,' +
            '-82.0833359084557 44.0833320331081,' +
            '-82.000000033378 44.0833320331082,' +
            '-82.000000033378 43.9999999705306)))')
    roi = GEOSGeometry(grid.replace('\n',''), srid=4326)

    return(roi)

def assign_pts_to_project(project, points):
    """
    """
    for pt in points:
        SamplePointFactory.create(project=project,
                                    geom=GEOSGeometry(pt,srid=4326))


@pytest.fixture
def project_disjoint():
    """create a project with samples that do not fall in our region of
    interest, but do fall all around it.
    """
    prj_cd = 'LHA_IA13_DIS'
    project = ProjectFactory.create(prj_cd=prj_cd)
    #these are centroids of four grids north, south, east and west of the roi
    pts = ['POINT(-82.0416679351682 43.9583319806175)',
           'POINT(-82.0416679337938 44.1249979556483)',
           'POINT(-82.1249999941107 44.0416640136496)',
           'POINT(-81.9583320623296 44.0416640159647)']

    assign_pts_to_project(project, pts)

    return(project)


@pytest.fixture
def project_all_in():
    """create a project with samples all fall with in our region of
    interest.
    """
    prj_cd = 'LHA_IA13_INN'
    project = ProjectFactory.create(prj_cd=prj_cd)

    #these are four randomly selected points that all fall within the roi
    pts = ['POINT(-82.081126628131 44.000970817096)',
           'POINT(-82.0456637754061 44.0649121962459)',
           'POINT(-82.024922507764 44.0171801372301)',
           'POINT(-82.0017671634393 44.0513359855003)']
    assign_pts_to_project(project, pts)

    return(project)


@pytest.fixture
def project_some_in():
    """create a project with some samples in our region of
    interest, and some outside.
    """
    prj_cd = 'LHA_IA13_LAP'
    project = ProjectFactory.create(prj_cd=prj_cd)
    #grid 2926 - north of roi

    #two of these points are in the roi, two are out
    pts = ['POINT(-82.081126628131 44.000970817096)',
           'POINT(-82.0456637754061 44.0649121962459)',
           'POINT(-82.1249999941107 44.0416640136496)',
           'POINT(-81.9583320623296 44.0416640159647)']
    assign_pts_to_project(project, pts)

    return(project)


@pytest.fixture
def four_projects():
    """To test the filters, we need four different projects of different
    types and years.  Four projects of two types run in four different
    years should provide us with enought contrast to test the most
    common combinations.  They will all use the same points, all of
    which will be contained within the roi.

    """

    offshore = ProjTypeFactory(project_type='Offshore')
    comcatch = ProjTypeFactory(project_type='ComCatch')

    prj_cds = ['LHA_IA90_002','LHA_CF95_555','LHA_IA00_002','LHA_CF05_555']
    prj_types=[offshore, comcatch, offshore, comcatch]


    pts = ['POINT(-82.081126628131 44.000970817096)',
           'POINT(-82.0456637754061 44.0649121962459)',
           'POINT(-82.024922507764 44.0171801372301)',
           'POINT(-82.0017671634393 44.0513359855003)']

    for x, y in zip(prj_cds, prj_types):
        project = ProjectFactory.create(prj_cd=x, project_type=y)
        assign_pts_to_project(project, pts)





def test_find_project_roi_not_polygon():
    """if the region of interest is not a polygon or multipolygon, the
    function find_projects_roi should return a two element dictionay
    containing empty lists for 'overlapping' and 'contained', but should
    not throw an error.
    """
    roi = GEOSGeometry('POINT(5 23)')
    projects = find_roi_projects(roi)
    assert sorted(projects.keys()) == ['contained', 'map_points', 'overlapping']
    assert projects.values() == [[], [], []]

    roi = GEOSGeometry('LINESTRING(5 23, 10 30 )')
    projects = find_roi_projects(roi)
    assert sorted(projects.keys()) == ['contained', 'map_points', 'overlapping']
    assert projects.values() == [[], [], []]

    #should even work for objects that have not geom_type() method.
    roi = 'foobar'
    projects = find_roi_projects(roi)
    assert sorted(projects.keys()) == ['contained', 'map_points', 'overlapping']
    assert projects.values() == [[], [], []]


@pytest.mark.django_db
def test_find_project_roi_contained(roi, project_all_in):
    """If there are samples from one or more projects that are completely
    contained within the roi, function roi should return a two element
    dictionary containing an empty list for 'overlapping' and a list
    'contained with one element for each project code.

    """
    #we need a region of interest, a project, and some sample points
    #that all fall within the

    projects = find_roi_projects(roi)
    assert sorted(projects.keys()) == ['contained', 'map_points', 'overlapping']
    assert projects['contained'] == [project_all_in]
    assert projects['overlapping'] == []

    points = projects['map_points']
    assert len(points) > 0


@pytest.mark.django_db
def test_find_project_roi_overlapping(roi, project_some_in):
    """If there are samples from one or more projects that are partially
    contained within the roi, function roi should return a two element
    dictionary containing an empty list for 'contains' and a list
    'overlapping' with one element for each project code.
    """

    projects = find_roi_projects(roi)
    assert sorted(projects.keys()) == ['contained', 'map_points', 'overlapping']
    assert projects['contained'] == []
    assert projects['overlapping'] == [project_some_in]

    points = projects['map_points']
    assert len(points) > 0


@pytest.mark.django_db
def test_find_project_roi_disjoint(roi, project_disjoint):
    """If there are samples from one or more projects that do not occur in
    the roi, function should return a two element dictionary
    containing an empty lists for 'contains' and 'overlapping'.

    """

    projects = find_roi_projects(roi)
    assert sorted(projects.keys()) == ['contained', 'map_points', 'overlapping']
    assert projects['contained'] == []
    assert projects['overlapping'] == []

    points = projects['map_points']
    assert len(points) == 0


@pytest.mark.django_db
def test_find_project_roi_both_contained_and_overlapping(roi,
                                                         project_some_in,
                                                         project_all_in,
                                                         project_disjoint):

    """If there are samples from one or more projects that are partially
    contained within the roi and other samples from a project that are
    entirely contained within the roi, the function find_projects_roi
    should return a two element dictionary containing list for
    'contains' and 'overlapping'.  The lists should be mutually exclusive.
    code.

    """

    projects = find_roi_projects(roi)
    assert sorted(projects.keys()) == ['contained', 'map_points', 'overlapping']
    assert projects['contained'] == [project_all_in]
    assert projects['overlapping'] == [project_some_in]


@pytest.mark.django_db
def test_find_project_roi_filter_project_type(roi, four_projects):
    '''If a list of project types are provided, they should be used to
    filter the projects returned by roi'''

    offshore = ProjectType.objects.get(project_type='Offshore')
    projects = find_roi_projects(roi, project_types=[offshore.id])
    prj_cds = [x.prj_cd for x in projects['contained']]
    assert sorted(prj_cds) == sorted(['LHA_IA90_002', 'LHA_IA00_002'])


@pytest.mark.django_db
def test_find_project_roi_filter_first_year(roi, four_projects):
    '''If a first year is provided, only projects run since that year
    should be returned'''

    projects = find_roi_projects(roi, first_year=2000)
    prj_cds = [x.prj_cd for x in projects['contained']]
    assert sorted(prj_cds) == sorted(['LHA_IA00_002','LHA_CF05_555'])


@pytest.mark.django_db
def test_find_project_roi_filter_last_year(roi, four_projects):
    '''If a last year is provided, only projects run on or before that year
    should be returned'''
    projects = find_roi_projects(roi, last_year=1999)
    prj_cds = [x.prj_cd for x in projects['contained']]
    assert sorted(prj_cds) == sorted(['LHA_IA90_002','LHA_CF95_555'])


@pytest.mark.django_db
def test_find_project_roi_filter_first_last_year(roi, four_projects):
    '''If both a first and last year are provided, only projects run
    between those years should be returned
    '''
    projects = find_roi_projects(roi, first_year = 1995, last_year=2000)
    prj_cds = [x.prj_cd for x in projects['contained']]
    assert sorted(prj_cds) == sorted(['LHA_CF95_555','LHA_IA00_002'])
