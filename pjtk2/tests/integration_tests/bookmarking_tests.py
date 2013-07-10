import unittest

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase
from django.conf import settings

from pjtk2.tests.factories import *


class ProjectBookmarkingTestCase(TestCase):
    '''User should be able to bookmark and unbookmark projects'''

    def setUp(self):        

        #create a differnt user that will be the manager
        self.user = UserFactory(username = 'gconstansa',
                                first_name = 'George',
                                last_name = 'Costansa')

        self.employee = EmployeeFactory(user=self.user)


        
        #create two projects, one that will be bookmarked, and one that
        #isn't.  
        self.client = Client()        
        #self.user = UserFactory()
        self.project1 = ProjectFactory(
            PRJ_CD="LHA_IA12_222",
            owner = self.user)
        self.project2 = ProjectFactory(
            PRJ_CD = "LHA_IA12_111",
            prj_nm = "An approved project",
            prj_ldr = self.user,
            owner = self.user)
        self.project2.Approved = True
        self.project2.save()

    def test_bookmarking(self):        

        #navigate to myproject view
        #bookmark project list should be empty
        #navigate to project1 and bookmark it
        #return to my projects view
        #bookmarked project should be in list
        #unbookmarked project shouldn't be
        #retrun to project detail page, unbookmark project
        #return to myprojects - bookmark list should be empty

        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('MyProjects'),follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "my_projects.html")
        self.assertContains(response, 'Bookmarks')
        #self.assertNotContains(response, self.project1.PRJ_CD)        
        #self.assertNotContains(response, self.project2.PRJ_CD)                


    def test_bookmarking_view(self):

        projectCnt = Project.objects.all().count()
        bookmarkCnt = Bookmark.objects.filter(user=self.user).count()
        
        self.assertEqual(projectCnt,2)
        self.assertEqual(bookmarkCnt,0)

        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)
        
        #bookmark a project
        response = self.client.get(
             reverse('Bookmark_Project', args=(self.project1.slug,)),
                     follow=True) 
        #we should be re-directed back to the project detail page
        self.assertTemplateUsed(response, 'projectdetail.html')
        self.assertContains(response, 'Project Detail')
        self.assertContains(response, self.project1.PRJ_CD)
        self.assertContains(response, self.project1.prj_nm)
        self.assertContains(response, self.project1.prj_ldr)
                
        bookmarks = Bookmark.objects.filter(user=self.user)
        self.assertEqual(bookmarks.count(),1)
        bookmark=bookmarks[0]
        self.assertEqual(bookmark.project.PRJ_CD,self.project1.PRJ_CD)
        self.assertEqual(bookmark.project.prj_nm,self.project1.prj_nm)        

    def test_unbookmarking_confirm_view(self):
        '''Verify that we get the confirm bookmark page when we first try and
        delete a book mark (request==get)'''

        projectCnt = Project.objects.all().count()
        bookmarkCnt = Bookmark.objects.filter(user=self.user).count()
        
        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)        
        #bookmark a project
        response = self.client.get(
             reverse('Bookmark_Project', args=(self.project1.slug,)),
                     follow=True) 
                
        bookmarks = Bookmark.objects.filter(user=self.user)
        self.assertEqual(bookmarks.count(),1)

        #now unbookmark the same project
        response = self.client.get(
             reverse('Unbookmark_Project', args=(self.project1.slug,)),
                     follow=True) 
        #this is get request to a project that has a book mark,
        #we should be redirect to the confirmation page.
        self.assertTemplateUsed(response, 'confirm_bookmark_delete.html')
        self.assertContains(response, self.project1.PRJ_CD)
        self.assertContains(response, "Delete bookmark")

    def test_unbookmarking_post_view(self):
        '''confirm that you actaully can delete a bookmark with a post request.'''
        projectCnt = Project.objects.all().count()
        bookmarkCnt = Bookmark.objects.filter(user=self.user).count()
        
        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)
        
        #bookmark a project
        response = self.client.get(
             reverse('Bookmark_Project', args=(self.project1.slug,)),
                     follow=True) 

        #we should be re-directed back to the project detail page
        #after a post request
        response = self.client.post(
             reverse('Unbookmark_Project', args=(self.project1.slug,)),
                     follow=True) 
        self.assertTemplateUsed(response, 'projectdetail.html')
        self.assertContains(response, 'Project Detail')
        self.assertContains(response, self.project1.PRJ_CD)
        self.assertContains(response, self.project1.prj_nm)
        self.assertContains(response, self.project1.prj_ldr)
        
        bookmarks = Bookmark.objects.filter(user=self.user)
        self.assertEqual(bookmarks.count(),0)
                
        
    def tearDown(self):
        self.project1.delete()
        self.project2.delete()

        self.user.delete()


