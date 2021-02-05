"""=============================================================
 c:/Users/COTTRILLAD/1work/Python/djcode/apps/pjtk2/pjtk2/tests/api/test_project_abstracts.py
 Created: 04 Feb 2021 14:24:19

 DESCRIPTION:

  The tests in this script ensure that the project abstract endpoint
  works as expected.  The endpoint should return the detail of a
  single project if a slug is provided, and retun a list of project
  details otherwise.

   the list of prejects uses the same filter as project filters. they
   are not all tested, here, but the filter for lake and year should be.

  The endpoint should not include projects that have been canceled or
  not approved

  If a project has images assoicated with it, they should be included.

  The list of images should only inlcude images where report=True.

 A. Cottrill
=============================================================

"""

import pytest

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse

from rest_framework import status

from pjtk2.models import Project, ProjectType
from pjtk2.api.serializers import (
    ProjectSerializer,
    ProjectTypeSerializer,
    UserSerializer,
)
from pjtk2.tests.factories import (
    LakeFactory,
    MilestoneFactory,
    ProjectFactory,
    ProjTypeFactory,
    UserFactory,
    ProjectImageFactory,
)

from rest_framework.test import APITestCase

User = get_user_model()


@pytest.fixture
def dbsetup():

    # we need set up 5 projects, on canceled and one that has not been
    # approved - these two will never appear in any list.
    # two will be on one lake on two diffent years,
    # the last will be in a different lake.

    homer = UserFactory(username="hsimpson", first_name="Homer", last_name="Simpson")

    huron = LakeFactory(lake_name="Huron", abbrev="HU")
    superior = LakeFactory(lake_name="Superior", abbrev="SU")

    project1 = ProjectFactory.create(
        prj_cd="LHA_IA11_123",
        prj_ldr=homer,
        abstract="This is something about the project.",
        prj_nm="Homer's Odyssey",
        lake=huron,
    )

    ProjectFactory.create(prj_cd="LHA_IA11_666", lake=huron)
    ProjectFactory.create(prj_cd="LHA_IA12_999", lake=huron)
    ProjectFactory.create(prj_cd="LSA_CF12_999", lake=superior)

    ProjectFactory.create(prj_cd="LHA_IA11_000", lake=huron, cancelled=True)

    # add some images to project 1.  The first two should be included in the report
    # and should be in the response. The third should not.

    ProjectImageFactory(project=project1, caption="This is image 1.", report=True)
    ProjectImageFactory(project=project1, caption="This is image 2.", report=True)
    ProjectImageFactory(
        project=project1,
        caption="This is image 3 - Not to be included in the report.",
        report=False,
    )


def test_project_abstracts_api_post_put_delete(client):
    """the project list api is currently readonly - any other request
    type should throw an error."""

    url = reverse("api:project_abstract-list")
    data = {"name": "FooBar"}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


parameters = [
    (
        None,
        ["LHA_IA11_123", "LHA_IA11_666", "LSA_CF12_999", "LHA_IA12_999"],
        [
            "LHA_IA11_000",
        ],
    ),
    (
        {"lake": "SU"},
        [
            "LSA_CF12_999",
        ],
        ["LHA_IA11_123", "LHA_IA11_666", "LHA_IA11_000", "LHA_IA12_999"],
    ),
    (
        {"year": 2012},
        ["LSA_CF12_999", "LHA_IA12_999"],
        [
            "LHA_IA11_000",
            "LHA_IA11_123",
            "LHA_IA11_666",
        ],
    ),
    (
        {"year": 2012, "lake": "HU"},
        ["LHA_IA12_999"],
        [
            "LHA_IA11_000",
            "LHA_IA11_123",
            "LHA_IA11_666",
            "LSA_CF12_999",
        ],
    ),
]


@pytest.mark.django_db
@pytest.mark.parametrize("filter, expected, excluded", parameters)
def test_abstract_list_and_filters(client, dbsetup, filter, expected, excluded):
    """the project list api is currently readonly - any other request
    type should throw an error."""

    url = reverse("api:project_abstract-list")
    if filter:
        response = client.get(url, filter)
    else:
        response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    data = response.data["results"]
    observed = [x.get("prj_cd") for x in data]

    assert len(observed) == len(expected)
    for item in expected:
        assert item in observed
    for item in excluded:
        assert item not in observed


@pytest.mark.django_db
def tests_project_abstract_detail(client, dbsetup):
    """verify that the abstract detail contains all of the required elements:"""

    project = Project.objects.get(slug="lha_ia11_123")

    url = reverse("api:project_abstract-detail", kwargs={"slug": project.slug})
    response = client.get(url)

    expected_keys = [
        "year",
        "prj_cd",
        "slug",
        "prj_nm",
        "prj_date0",
        "prj_date1",
        "project_type",
        "project_leader",
        "abstract",
        "images",
    ]

    for key in expected_keys:
        assert key in response.data.keys()

    # check some of the values too:
    assert response.data["project_leader"] == "Homer Simpson"

    assert response.data["prj_cd"] == project.prj_cd
    assert response.data["prj_nm"] == project.prj_nm
    assert response.data["abstract"] == project.abstract


@pytest.mark.django_db
def test_abstract_images(client, dbsetup):
    """If a project has images associated with, the response should
    include a nested object that contains attributes about each image.

    """
    project = Project.objects.get(slug="lha_ia11_123")

    url = reverse("api:project_abstract-detail", kwargs={"slug": project.slug})
    response = client.get(url)

    images = response.data["images"]

    assert len(images) == 2
    captions = [x["caption"] for x in images]
    assert "This is image 1." in captions
    assert "This is image 2." in captions


@pytest.mark.django_db
def test_abstract_only_includes_report_images(client, dbsetup):
    """The list of images should only inlcude images where report=True,
    other images should not be included in the response.

    This test is very similar to the previous test, but it explicitly
    tests the filtering functionality of a nested serializer using Prefetch().

    """

    project = Project.objects.get(slug="lha_ia11_123")

    url = reverse("api:project_abstract-detail", kwargs={"slug": project.slug})
    response = client.get(url)

    images = response.data["images"]
    captions = [x["caption"] for x in images]

    img_caption = "This is image 3 - Not to be included in the report."
    assert img_caption not in captions
