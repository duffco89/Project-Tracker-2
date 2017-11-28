import pytest

#=================================
#       Points In ROI

def test_points_in_roi_api_get_put_delete():
    """the points api is currently readonly, but requires a post request
    (which holds the roi). Any other request type should throw an
    error.

    """
    assert 0==1

def test_points_in_roi_api_post_good_roi_wkt():
    """If we pass in a valid roi as wkt, the api should return a list of
    sample points contained in the roi.  It will not include points
    outside of the roi.

    """
    assert 0==1


def test_points_in_roi_api_post_good_roi_json():
    """If we pass in a valid roi as json, the api should return a list of sample
    points contained in the roi.  It will not include points outside of
    the roi.
    """
    assert 0==1


def test_points_in_roi_api_post_no_points():
    """If we pass in a valid roi, that does not include any sample points,
    the api should return a message indicating that no points were found.

    """
    assert 0==1

def test_points_in_roi_api_post_bad_roi_line():
    """If the roi in the post request does not form a valid polygon, an
    appropriate error should be thrown.

    """
    assert 0==1

def test_points_in_roi_api_post_bad_roi_point():
    """If the roi in the post request does not form a valid polygon, an
    appropriate error should be thrown.

    """
    assert 0==1

def test_points_in_roi_api_post_bad_roi_jibberish():
    """If the roi in the post request does not form a valid polygon, an
    appropriate error should be thrown.

    """
    assert 0==1

def test_points_in_roi_api_post_missing_roi():
    """If the post request does not have a roi element an appropriate
    error should be thrown.

    """
    assert 0==1



#=====================================
#     Projects Completely In ROI


def test_projects_contained_in_roi_api_get_put_delete():
    """the projects contained in api is currently readonly, but requires a
    post request (which holds the roi). Any other request type should
    throw an error.

    """
    assert 0==1

def test_projects_contained_in_roi_api_post_good_roi_wkt():
    """If we pass in a valid roi as wkt, the api should return a list of
    projects that are completely contained in the roi.  It will not
    include projects without any points, or with points outside of the roi.

    """
    assert 0==1


def test_projects_contained_in_roi_api_post_good_roi_json():
    """If we pass in a valid roi as json, the api should return a list of
    projects that are completely contained in the roi.  It will not
    include projects without any points, or with points outside of the roi.
    """
    assert 0==1


def test_projects_contained_in_roi_api_post_no_points():
    """If we pass in a valid roi, that does not include any sample points,
    the api should return a message indicating that no projects were
    found in the roi.

    """
    assert 0==1

def test_projects_contained_in_roi_api_post_bad_roi_line():
    """If the roi in the post request does not form a valid polygon, an
    appropriate error should be thrown.
    """
    assert 0==1

def test_projects_contained_in_roi_api_post_bad_roi_point():
    """If the roi in the post request does not form a valid polygon (just
    a point in this test), an appropriate error should be thrown.

    """
    assert 0==1

def test_projects_contained_in_roi_api_post_bad_roi_jibberish():
    """If the roi in the post request does not form a valid polygon, (just
    jubberish in this test) an appropriate error should be thrown.
    """
    assert 0==1

def test_projects_contained_in_roi_api_post_missing_roi():
    """If the post request does not have a roi element an appropriate
    error should be thrown.

    """
    assert 0==1


#=====================================
#    Projects Partially In ROI

def test_projects_partially_contained_in_roi_api_get_put_delete():
    """the projects partially contained in api is currently readonly, but
    requires a post request (which holds the roi). Any other request
    type should throw an error.

    """
    assert 0==1


def test_projects_partially_contained_in_roi_api_post_good_roi_wkt():
    """If we pass in a valid roi as wkt, the api should return a list of
    projects that are partially contained in the roi.  It will not
    include projects without any points, or projects with all of their
    points inside the roi.

    """
    assert 0==1


def test_projects_partially_contained_in_roi_api_post_good_roi_json():
    """If we pass in a valid roi as json, the api should return a list of
    projects that are partially contained in the roi.  It will not
    include projects without any points, or projects with all of their
    points in the roi.

    """
    assert 0==1


def test_projects_partially_contained_in_roi_api_post_no_points():
    """If we pass in a valid roi, that does not include any sample points,
    the api should return a message indicating that no samples from
    any project were found in the roi.

    """
    assert 0==1

def test_projects_partially_contained_in_roi_api_post_bad_roi_line():
    """If the roi in the post request does not form a valid polygon (just
    a line in this test), an appropriate error should be thrown.

    """
    assert 0==1

def test_projects_partially_contained_in_roi_api_post_bad_roi_point():
    """If the roi in the post request does not form a valid polygon (just
    a point in this test), an appropriate error should be thrown.

    """
    assert 0==1

def test_projects_partially_contained_in_roi_api_post_bad_roi_jibberish():
    """If the roi in the post request does not form a valid polygon, (just
    jubberish in this test) an appropriate error should be thrown.
    """
    assert 0==1

def test_projects_partially_contained_in_roi_api_post_missing_roi():
    """If the post request does not have a roi element an appropriate
    error should be thrown.

    """
    assert 0==1
