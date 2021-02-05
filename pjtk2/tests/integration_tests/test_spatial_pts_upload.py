"""=============================================================
 c:/Users/COTTRILLAD/1work/Python/djcode/apps/pjtk2/pjtk2/tests/integration_tests/test_spatial_pts_upload.py
 Created: 05 Feb 2021 09:11:50

 DESCRIPTION:

  The tests in this file verify that the interface that allows users
  to upload spatial data works as expected:

  + only available to staff who can edit the project (owner, admin, or
  manager)

  + acceps csv or xlxs

  + append or replace

  + throws an error if the uploaded file does not have a header with
    the appopriate names

  + captures malformed points or those outside of GL Basin (for now)

  + point label is required

  + includes helpful instructions describing what spatial data is
  relevant (creels vs field project vs synthesis)

  + upload format should match format returned by api endpoint - will
  allow us to download, edit and then re-upload points.

  + consider adding download to xlsx button on each project page if
  spatial data exists.

 A. Cottrill
=============================================================

"""


import pytest


def test_upload_spatial_points_button_on_detail_page():
    """The button to upload spatial data should be available to
    authenticated users on the project detail page."""

    assert 0 == 1


def test_download_spatial_points_button_on_detail_page():
    """consider adding download to xlsx button on each project page if
    spatial data exists."""

    assert 0 == 1


def test_point_upload_authentication():
    """The form should not be accessible to users who cannot edit the
    project, or are annonymous.

    """

    assert 0 == 1


def test_point_bad_header():
    """If the uploaded file does not have the correcting headings in the
    first row, return an appropriate error message.

    """

    assert 0 == 1


def test_point_bad_latlong():
    """IF the coordinates are cannot be converted to points, an
    appropriate error should be returned.

    """

    assert 0 == 1


def test_point_out_of_bounds():
    """If one or more of the points in the uploaded file are outside the
    bounds of the lake associated with the project, then return an
    appropriate error message.  For now, we will use the bounding box
    for the lake, but it could be more refined in the future.

    """

    assert 0 == 1


def test_points_missing_label():
    """Every point must have label - it labels are missing or empty
    strings, raise an error.

    """

    assert 0 == 1


def test_accepts_xlsx_or_csv():
    """The form should not accept any other file time."""
    assert 0 == 1


def test_accepts_append_or_replace_is_required():
    """The form should not accept any other file time."""
    assert 0 == 1


def test_append_xlsx():
    """if the append option is specified when the data is submitted as an
    xlsx file, the points should be added to ones already present."""
    assert 0 == 1


def test_replace_xlsx():
    """if the replace option is specified when the data is submitted as an
    xlsx file, the points should replace any that are already present."""
    assert 0 == 1


def test_append_csv():
    """if the append option is specified when the data is submitted as an
    csv file, the points should be added to ones already present."""
    assert 0 == 1


def test_replace_csv():
    """if the replace option is specified when the data is submitted as an
    csv file, the points should replace any that are already present."""
    assert 0 == 1
