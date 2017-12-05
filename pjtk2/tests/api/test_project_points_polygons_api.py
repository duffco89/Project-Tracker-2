
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse

from rest_framework import status

from pjtk2.models import Project
from pjtk2.api.serializers import (ProjectPolygonSerializer,
                                   ProjectPointSerializer)
from pjtk2.tests.factories import *

from rest_framework.test import APITestCase


class ProjectAPITest(APITestCase):

    def setUp(self):

        self.factory = RequestFactory()

        #we need to create some models with different years - starting
        #with the current year.

        prj_cd = "LHA_IA16_INN"
        self.project1 = ProjectFactory.create(prj_cd=prj_cd,
                                              prj_nm = "All In Roi")

        #these are four randomly selected points that all fall within the roi
        pts = ['POINT(-82.081126628131 44.000970817096)',
               'POINT(-82.0456637754061 44.0649121962459)',
               'POINT(-82.024922507764 44.0171801372301)',
               'POINT(-82.0017671634393 44.0513359855003)']
        for i,pt in enumerate(pts):
            SamplePointFactory.create(project=self.project1,
                                      sam="In-{}".format(i),
                                      geom = GEOSGeometry(pt))

        self.project1.update_convex_hull()


        prj_cd = "LHA_IA16_000"
        self.project4 = ProjectFactory.create(prj_cd=prj_cd,
                                              prj_nm = "No Points")



    #===================
    #PROJECT POINTS

    def test_project_points_api_get_good_project_code(self):
        """The project points api should return a series of geojson points
        corresponding to sampling locations associated with a
        project.
        """

        slug = self.project1.slug
        url = reverse('api:project_points', kwargs={'slug':slug})

        request = self.factory.get(url)
        response = self.client.get(url)

        # get data from db
        points = SamplePoint.objects.filter(project__slug=slug)
        serializer = ProjectPointSerializer(points, many=True,
                                       context={'request': request})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


    def test_project_points_api_get_bad_project_code(self):
        """If we try to access the project points api with a malformed project
        code it will return an error.

        """

        slug = 'LHA_XX15_X01'
        url = reverse('api:project_points', kwargs={'slug':slug})
        response = self.client.get(url.replace("X",""))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_project_points_api_get_project_code_doesnot_exist(self):
        """If we try to access the project points api for a project that
        does not exists, code it will return a 404 error.
        """

        slug = 'LHA_IA15_ABC'
        url = reverse('api:project_points', kwargs={'slug':slug})
        request = self.factory.get(url)
        response = self.client.get(url)

        points = SamplePoint.objects.filter(project__slug=slug)
        serializer = ProjectPointSerializer(points, many=True,
                                       context={'request': request})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        self.assertEqual(len(response.data), 0)
        self.assertEqual(len(serializer.data), 0)


    def test_project_points_api_get_project_code_without_points(self):
        """If we try to access the project points api for a project without
        sample points, it will handle it gracefully.
        """

        slug = self.project4.slug
        url = reverse('api:project_points', kwargs={'slug':slug})
        request = self.factory.get(url)
        response = self.client.get(url)

        points = SamplePoint.objects.filter(project__slug=slug)
        serializer = ProjectPointSerializer(points, many=True,
                                       context={'request': request})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        self.assertEqual(len(response.data), 0)
        self.assertEqual(len(serializer.data), 0)


    def test_project_points_api_post_put_delete(self):
        """the project points api is currently readonly - any other request
        type should throw an error.

        """

        slug = self.project4.slug
        url = reverse('api:project_points', kwargs={'slug':slug})
        data = {'sam': 'Test-1'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)



    #=================================
    #     PROJECT POLYGON

    def test_project_polygon_api_get_good_project_code(self):
        """The project polygon api should return a series of geojson polygon
        corresponding to sampling locations associated with a
        project.
        """

        slug = self.project1.slug
        url = reverse('api:project_polygon', kwargs={'slug':slug})

        request = self.factory.get(url)
        response = self.client.get(url)

        # get data from db
        polygon = ProjectPolygon.objects.filter(project__slug=slug)
        serializer = ProjectPolygonSerializer(polygon, many=True,
                                       context={'request': request})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)



    def test_project_polygon_api_get_bad_project_code(self):
        """If we try to access the project polygon api with a malformed project
        code it will return an error.
        """

        slug = 'LHA_XX15_X01'
        url = reverse('api:project_polygon', kwargs={'slug':slug})
        response = self.client.get(url.replace("X",""))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_project_polygon_api_get_project_code_doesnot_exist(self):
        """If we try to access the project polygon api for a project that
        does not exists, code it will return an empty array.
        """

        slug = 'LHA_IA15_ABC'
        url = reverse('api:project_polygon', kwargs={'slug':slug})
        request = self.factory.get(url)
        response = self.client.get(url)

        # get data from db
        polygon = ProjectPolygon.objects.filter(project__slug=slug)
        serializer = ProjectPolygonSerializer(polygon, many=True,
                                       context={'request': request})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        self.assertEqual(len(response.data), 0)
        self.assertEqual(len(serializer.data), 0)


    def test_project_polygon_api_get_project_code_without_polygon(self):
        """If we try to access the project polygon api for a project without
        sample polygon, it will handle it gracefully.
        """


        slug = self.project4.slug
        url = reverse('api:project_polygon', kwargs={'slug':slug})
        request = self.factory.get(url)
        response = self.client.get(url)

        # get data from db
        polygon = ProjectPolygon.objects.filter(project__slug=slug)
        serializer = ProjectPolygonSerializer(polygon, many=True,
                                       context={'request': request})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

        self.assertEqual(len(response.data), 0)
        self.assertEqual(len(serializer.data), 0)




    def test_project_polygon_api_post_put_delete(self):
        """the project polygon api is currently readonly - any other request
        type should throw an error.

        """

        slug = self.project4.slug
        url = reverse('api:project_polygon', kwargs={'slug':slug})
        data = {'sam': 'Test-1'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
