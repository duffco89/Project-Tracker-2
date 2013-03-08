import unittest

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase

from pjtk2.tests.factories import *


#Views
class IndexViewsTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('')
        self.assertEqual(resp.status_code,200)


class CreateManagerTestCase(unittest.TestCase):

    def setUp(self):
        managerGrp = Group(name='manager')
        managerGrp.save()
         
        self.manager = UserFactory.create(username="bosshog")         
        self.manager.groups.add(managerGrp)

    def test_is_manager(self):

        grpcnt =  self.manager.groups.filter(name='manager').count()         
        self.assertTrue(grpcnt >0)
         
class LoginTestCase(unittest.TestCase):
    def setUp(self):        
        self.client = Client()
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 
                                             'johnpassword')
        
    def testLogin(self):
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)



        
