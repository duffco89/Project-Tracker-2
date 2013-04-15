import unittest
import pdb

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase

from pjtk2.tests.factories import *


#Views
class IndexViewTestCase(TestCase):
    '''verfiy that we can view the site index page'''
    def test_index(self):
        response = self.client.get('')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertContains(response, 'Site Index')
        self.assertContains(response, 'Project List')        
        self.assertContains(response, 'Approved Project List')                
        self.assertContains(response, 'Approve Projects')                        
        

class ProjectListTestCase(TestCase):
    '''verfiy that we view the  project list, but only after logging-in'''

    def setUp(self):        
        self.client = Client()        
        self.user = UserFactory()
    
    def test_without_Login(self):
        '''if we try to view the page without logging in, we should be
        re-directed to the login page'''
        response = self.client.get(reverse('ProjectList'), follow=True)
        self.assertEqual(response.status_code,200)
        redirectstring = "%s?next=%s" % (reverse('login'),reverse('ProjectList'))
        self.assertRedirects(response, redirectstring)

    def test_bad_Password_Login(self):
        '''verify that the login actually stops someone'''
        login = self.client.login(username=self.user.username, password='abcd')
        self.assertFalse(login)
        
    def test_with_Login(self):
        '''if we login with a valid user, we will be allowed to view
        the page'''
        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('home')) 
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('ProjectList'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ProjectList.html')
        self.assertContains(response, 'Projects')

    def tearDown(self):
        self.user.delete()
        
        
class CreateManagerTestCase(TestCase):
    '''verify that we can create a user that belongs to the 'manager'
    group'''
    def setUp(self):
        self.user = UserFactory()
        managerGrp, created = Group.objects.get_or_create(name='manager')         
        self.user.groups.add(managerGrp)
    
    def test_is_manager(self):
        grpcnt =  self.user.groups.filter(name='manager').count()         
        self.assertTrue(grpcnt >0)



        
    def tearDown(self):
        self.user.delete()
        #managerGrp.delete()

        
class LoginTestCase(TestCase):
    '''verify that we can login using a 'User' object'''
    def setUp(self):        
        self.client = Client()
        self.user = User.objects.create_user('john2', 'lennon@thebeatles.com', 
                                             'johnpassword')
        
    def testLogin(self):
        self.client.login(username='john2', password='johnpassword')
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.user.delete()



        
class LogoutTestCase(TestCase):
    '''verify that we can logout using a 'User' object'''
    def setUp(self):        
        self.client = Client()
        self.user = UserFactory(username='hsimpson')
        
    def testLogin(self):
        login = self.client.login(username='hsimpson', password='abc')
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(login)

        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response,reverse('login'))
        self.assertTemplateUsed(response, 'auth/login.html')
        self.assertContains(response,"Username:")
        self.assertContains(response,"Password:")
                        
        
        #self.assertFalse(login)
        

    def tearDown(self):
        self.user.delete()


        
        
class FactoryBoyLoginTestCase(unittest.TestCase):
    '''verify that we can login a user created with factory boy.'''
    def setUp(self):        
        self.client = Client()
        self.user = UserFactory()
                
    def testLogin(self):
        self.client.login(username=self.user.username, password='abc')
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.user.delete()
        
#================================
#PROJECT DETAIL VIEWS

class ProjectDetailOwnerTestCase(TestCase):
    '''verify that a project owner can see the project and make
    appropriated changes, but not those available only to managers'''

    def setUp(self):        
        self.client = Client()        
        self.user = UserFactory()
        self.project = ProjectFactory(Owner = self.user)
            
    def test_with_Login(self):
        '''if we login with a valid user, we will be allowed to view
        the page'''
        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('ProjectDetail', 
                                        args=(self.project.slug,))) 
        self.assertEqual(response.status_code, 200)
        
        self.assertTemplateUsed(response, 'projectdetail.html')
        self.assertContains(response, 'Project Detail')
        self.assertContains(response, self.project.PRJ_CD)
        self.assertContains(response, self.project.PRJ_NM)
        self.assertContains(response, self.project.PRJ_LDR)
        self.assertContains(response, "Milestones")
        self.assertContains(response, "Reporting Requirements")

        #a user should be able to edit their own records, but not
        #update milestones.
        self.assertTrue(response.context['edit'])
        self.assertFalse(response.context['manager'])

    def test_without_Login(self):
        '''if we try to view page without logging in, we should be
        re-directed to the login page'''
        response = self.client.get(reverse('ProjectDetail', 
                                        args=(self.project.slug,)), follow=True)
        self.assertEqual(response.status_code,200)
        redirectstring = "%s?next=%s" % (reverse('login'),
                                         reverse('ProjectDetail', 
                                        args=(self.project.slug,))) 
        self.assertRedirects(response, redirectstring)

    def tearDown(self):
        self.project.delete()
        self.user.delete()


class ProjectDetailJoeUserTestCase(TestCase):
    '''verify that a user who is not the owner can see the project but
    will be unable to edit any fields, upload reports or set
    milestones.'''

    def setUp(self):        
        self.client = Client()        
        self.user = UserFactory(username = 'gconstansa',
                                first_name = 'George',
                                last_name = 'Costansa')
        #now create a project using a different user
        self.owner = UserFactory()
        self.project = ProjectFactory(Owner = self.owner)
            
    def test_with_Login(self):
        '''if we login with a valid user, we will be allowed to view
        the page'''
        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('ProjectDetail', 
                                        args=(self.project.slug,))) 
        self.assertEqual(response.status_code, 200)
        
        self.assertTemplateUsed(response, 'projectdetail.html')
        self.assertContains(response, 'Project Detail')
        self.assertContains(response, self.project.PRJ_CD)
        self.assertContains(response, self.project.PRJ_NM)
        self.assertContains(response, self.project.PRJ_LDR)
        self.assertContains(response, "Milestones")
        self.assertContains(response, "Reporting Requirements")

        #a user should be able to edit their own records, but not
        #update milestones.
        self.assertFalse(response.context['edit'])
        self.assertFalse(response.context['manager'])
        

    def test_without_Login(self):
        '''if we try to view page without logging in, we should be
        re-directed to the login page'''
        response = self.client.get(reverse('ProjectDetail', 
                                        args=(self.project.slug,)), follow=True)
        self.assertEqual(response.status_code,200)
        redirectstring = "%s?next=%s" % (reverse('login'),
                                         reverse('ProjectDetail', 
                                        args=(self.project.slug,))) 
        self.assertRedirects(response, redirectstring)

    def tearDown(self):
        self.project.delete()
        self.owner.delete()        
        self.user.delete()

        
        
class ProjectDetailManagerTestCase(TestCase):
    '''verify that a manager can see a project and be able to both
    edit the record and update milestones.'''

    def setUp(self):        
        self.client = Client()        
        self.user = UserFactory(username = 'gcostansa',
                                first_name = 'George',
                                last_name = 'Costansa')
        #make george the manager:
        managerGrp, created = Group.objects.get_or_create(name='manager')         
        self.user.groups.add(managerGrp)

        #now create a project using a different user
        self.owner = UserFactory()
        self.project = ProjectFactory(Owner = self.owner)
            
    def test_with_Login(self):
        '''if we login with a valid user, we will be allowed to view
        the page'''
        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('ProjectDetail', 
                                        args=(self.project.slug,))) 
        self.assertEqual(response.status_code, 200)
        
        self.assertTemplateUsed(response, 'projectdetail.html')
        self.assertContains(response, 'Project Detail')
        self.assertContains(response, self.project.PRJ_CD)
        self.assertContains(response, self.project.PRJ_NM)
        self.assertContains(response, self.project.PRJ_LDR)
        self.assertContains(response, "Milestones")
        self.assertContains(response, "Reporting Requirements")

        #a manager should be able to both edit the project and adjust
        #milestones accordingly.
        self.assertTrue(response.context['edit'])
        self.assertTrue(response.context['manager'])        

    def test_without_Login(self):
        '''if we try to view page without logging in, we should be
        re-directed to the login page'''
        response = self.client.get(reverse('ProjectDetail', 
                                        args=(self.project.slug,)), follow=True)
        self.assertEqual(response.status_code,200)
        redirectstring = "%s?next=%s" % (reverse('login'),
                                         reverse('ProjectDetail', 
                                        args=(self.project.slug,))) 
        self.assertRedirects(response, redirectstring)

    def tearDown(self):
        self.project.delete()
        self.owner.delete()        
        self.user.delete()
        



#================================
#APPROVED PROJECT LIST

class ApprovedProjectListUserTestCase(TestCase):
    '''All logged users should be able to see the list of approved
    projects, but only managers can makes updates to the list'''

    def setUp(self):        
        #create two projects, one that will be approved, and one that
        #isn't.  Only the approved one should appear in the list.
        self.client = Client()        
        self.user = UserFactory()
        self.project = ProjectFactory(Owner = self.user,
                                      Approved = False)
        self.project2 = ProjectFactory(
            PRJ_CD = "LHA_IA12_111",
            PRJ_NM = "An approved project",
            PRJ_LDR = self.user,
            Owner = self.user)
        #self.project2.Approved = True
        self.project2.save()
            
    def test_with_Login(self):
        '''if we login with a valid user, we will be allowed to view
        the page'''
        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('ApprovedProjectsList')) 
        self.assertEqual(response.status_code, 200)
        
        self.assertTemplateUsed(response, 'ApprovedProjectList.html')
        self.assertContains(response, 'Projects')
        #it should not contain the project that isn't approved
        self.assertNotContains(response, self.project.PRJ_CD)
        self.assertNotContains(response, self.project.PRJ_NM)

        #this one is approved and should be in the list
        self.assertContains(response, self.project2.PRJ_CD)
        self.assertContains(response, self.project2.PRJ_NM)

        #since this user is not a manager, she should not be able to
        #update the list
        self.assertNotContains(response, "Update this list")



    def test_without_Login(self):
        '''if we try to view page without logging in, we should be
        re-directed to the login page'''
        response = self.client.get(reverse('ApprovedProjectsList'),
                                   follow=True) 
        self.assertEqual(response.status_code,200)
        redirectstring = "%s?next=%s" % (reverse('login'),
                                         reverse('ApprovedProjectsList'))
        self.assertRedirects(response, redirectstring)

    def tearDown(self):
        self.project.delete()
        self.user.delete()
        

class ApprovedProjectListManagerTestCase(TestCase):
    ''' Managers should  be able to see the list of approved
    projects, and see the link to update the list'''

    def setUp(self):        
        #create two projects, one that will be approved, and one that
        #isn't.  Only the approved one should appear in the list.
        self.client = Client()        
        self.owner = UserFactory()
        self.project = ProjectFactory(Owner = self.owner,
                                      Approved = False)
        self.project2 = ProjectFactory(
            PRJ_CD = "LHA_IA12_111",
            PRJ_NM = "An approved project",
            PRJ_LDR = self.owner,
            Owner = self.owner)
        #self.project2.Approved = True
        self.project2.save()

        #create a differnt user that will be the manager
        self.user = UserFactory(username = 'gconstansa',
                                first_name = 'George',
                                last_name = 'Costansa')
        #make george the manager:
        managerGrp, created = Group.objects.get_or_create(name='manager')         
        self.user.groups.add(managerGrp)

            
    def test_with_Login(self):
        '''if we login with a valid user, we will be allowed to view
        the page'''
        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('ApprovedProjectsList')) 
        self.assertEqual(response.status_code, 200)
        
        self.assertTemplateUsed(response, 'ApprovedProjectList.html')
        self.assertContains(response, 'Projects')
        #it should not contain the project that isn't approved
        self.assertNotContains(response, self.project.PRJ_CD)
        self.assertNotContains(response, self.project.PRJ_NM)

        #this one is approved and should be in the list
        self.assertContains(response, self.project2.PRJ_CD)
        self.assertContains(response, self.project2.PRJ_NM)

        #since this user is a manager, she should be able to
        #update the list
        self.assertContains(response, "Update this list")



    def test_without_Login(self):
        '''if we try to view page without logging in, we should be
        re-directed to the login page'''
        response = self.client.get(reverse('ApprovedProjectsList'),
                                   follow=True) 
        self.assertEqual(response.status_code,200)
        redirectstring = "%s?next=%s" % (reverse('login'),
                                         reverse('ApprovedProjectsList'))
        self.assertRedirects(response, redirectstring)

    def tearDown(self):
        self.project.delete()
        self.user.delete()

        
#================================
#APPROVE PROJECTS

class ApproveProjectsManagerTestCase(TestCase):
    ''' Managers should  be able to see the list of approved
    projects, and see the link to update the list'''

    def setUp(self):        
        #create two projects, one that will be approved, and one that
        #isn't.  Only the approved one should appear in the list.
        self.client = Client()        
        self.owner = UserFactory()
        self.project1 = ProjectFactory(Owner = self.owner)
        self.project2 = ProjectFactory(
            PRJ_CD = "LHA_IA12_111",
            PRJ_NM = "An approved project",
            PRJ_LDR = self.owner,
            Owner = self.owner)
        self.project2.Approved = True
        self.project2.save()

        self.project3 = ProjectFactory(
            PRJ_CD = "LHA_IA12_999",
            PRJ_NM = "An approved and completed project",
            PRJ_LDR = self.owner,
            Owner = self.owner)
        self.project3.Approved = True
        self.project3.SignOff = True        
        self.project3.save()
        
        #create a differnt user that will be the manager
        self.user = UserFactory(username = 'gconstansa',
                                first_name = 'George',
                                last_name = 'Costansa')
        #make george the manager:
        managerGrp, created = Group.objects.get_or_create(name='manager')         
        self.user.groups.add(managerGrp)

            
    def test_with_Login(self):
        '''if we login with as a manager, we will be allowed to view
        the page'''
        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('ApproveProjects')) 
        self.assertEqual(response.status_code, 200)
        
        self.assertTemplateUsed(response, 'ApproveProjects.html')
        self.assertContains(response, 'Submitted Projects')

        #projects one and two are still active and should be in the list
        self.assertContains(response, self.project1.PRJ_CD)
        self.assertContains(response, self.project1.PRJ_NM)
        self.assertContains(response, self.project2.PRJ_CD)
        self.assertContains(response, self.project2.PRJ_NM)

        #it should not contain the third project it has been completed 
        # annd should not appear in this list
        self.assertNotContains(response, self.project3.PRJ_CD)
        self.assertNotContains(response, self.project3.PRJ_NM)

    def test_without_Login(self):
        '''if we try to view page without logging in, we should be
        re-directed to the login page'''
        response = self.client.get(reverse('ApproveProjects'),
                                   follow=True) 
        self.assertEqual(response.status_code,200)
        redirectstring = "%s?next=%s" % (reverse('login'),
                                         reverse('ApproveProjects'))
        self.assertRedirects(response, redirectstring)

    def tearDown(self):
        self.project1.delete()
        self.project2.delete()
        self.project3.delete()        
        self.user.delete()
        

class ApproveProjectsEmptyTestCase(TestCase):
    ''' Verify that a meaningful message is displayed if there aren't
    any project waiting to be approved.'''

    def setUp(self):        
        #create two projects, one that will be approved, and one that
        #isn't.  Only the approved one should appear in the list.
        self.client = Client()        
        
        #create a differnt user that will be the manager
        self.user = UserFactory(username = 'gconstansa',
                                first_name = 'George',
                                last_name = 'Costansa')
        #make george the manager:
        managerGrp, created = Group.objects.get_or_create(name='manager')         
        self.user.groups.add(managerGrp)

            
    def test_with_Login(self):
        '''if we login with as a manager, we will be allowed to view
        the page, but it should give us a pleasant notice that no
        projects are pending our approval
        .'''
        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('ApproveProjects')) 
        self.assertEqual(response.status_code, 200)
        
        self.assertTemplateUsed(response, 'ApproveProjects.html')
        self.assertContains(response, 'Submitted Projects')
        self.assertContains(response, 'no projects pending approval')

    def tearDown(self):
        self.user.delete()
        

class ApproveProjectsUserTestCase(TestCase):
    '''Users are not allowed to view the ApproveProjectsForm.  Verify
    that they are redirected to the ApprovedProjectList if they try.'''

    def setUp(self):        
        self.client = Client()        
        self.user = UserFactory()
            
    def test_with_Login(self):
        '''if we login with as a user, we will not be allowed to view
        the page, but instead will be redirect to the approved project list.'''
        
        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('ApproveProjects'),follow=True) 
        self.assertEqual(response.status_code, 200)

        self.assertRedirects(response, reverse('ApprovedProjectsList'))
        self.assertTemplateUsed(response, 'ApprovedProjectList.html')
        self.assertContains(response, 'Projects')
        
        #since this user is not a manager, she should not be able to
        #update the list
        self.assertNotContains(response, "Update this list")
        

        
    def tearDown(self):
        self.user.delete()
        


class ProjectBookmarkingTestCase(TestCase):
    '''User should be able to bookmark and unbookmark projects'''

    def setUp(self):        

        #create a differnt user that will be the manager
        self.user = UserFactory(username = 'gconstansa',
                                first_name = 'George',
                                last_name = 'Costansa')
        
        #create two projects, one that will be bookmarked, and one that
        #isn't.  
        self.client = Client()        
        self.user = UserFactory()
        self.project1 = ProjectFactory(
            PRJ_CD="LHA_IA12_222",
            Owner = self.user)
        self.project2 = ProjectFactory(
            PRJ_CD = "LHA_IA12_111",
            PRJ_NM = "An approved project",
            PRJ_LDR = self.user,
            Owner = self.user)
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
        self.assertContains(response, self.project1.PRJ_NM)
        self.assertContains(response, self.project1.PRJ_LDR)
                
        bookmarks = Bookmark.objects.filter(user=self.user)
        self.assertEqual(bookmarks.count(),1)
        bookmark=bookmarks[0]
        self.assertEqual(bookmark.project.PRJ_CD,self.project1.PRJ_CD)
        self.assertEqual(bookmark.project.PRJ_NM,self.project1.PRJ_NM)        

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
        self.assertContains(response, self.project1.PRJ_NM)
        self.assertContains(response, self.project1.PRJ_LDR)
        
        bookmarks = Bookmark.objects.filter(user=self.user)
        self.assertEqual(bookmarks.count(),0)
                
        
    def tearDown(self):
        self.project1.delete()
        self.project2.delete()

        self.user.delete()

class SisterProjectsTestCase(TestCase):
    '''Verify that the user can see and update sisters associated with projects'''


    def setUp(self):
        '''we will need three projects with easy to rember project codes'''
        self.user = UserFactory(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')
        

        self.ProjType = ProjTypeFactory()
        self.ProjType2 = ProjTypeFactory(Project_Type = "Nearshore Index")
        
        self.project1 = ProjectFactory.create(PRJ_CD="LHA_IA12_111", YEAR=2012, 
                                              Owner=self.user, slug='lha_ia12_111',
                                              ProjectType = self.ProjType)
        self.project2 = ProjectFactory.create(PRJ_CD="LHA_IA12_222", YEAR=2012, 
                                              Owner=self.user, slug='lha_ia12_222',
                                              ProjectType = self.ProjType)
        self.project3 = ProjectFactory.create(PRJ_CD="LHA_IA12_333", YEAR=2012, 
                                              Owner=self.user, slug='lha_ia12_333',
                                              ProjectType = self.ProjType)


    def test_sisterbtn(self):

        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)

        url = reverse('SisterProjects', args =(self.project1.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        self.assertTemplateUsed(response, 'SisterProjects.html')

        print "repsonse = %s" % response
        linktext = '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                                            args =(self.project2.slug,)), 
                                            self.project2.PRJ_CD)
        print "linktext = %s" % linktext
        self.assertContains(response, linktext)



    def tearDown(self):
        self.project1.delete()
        self.project2.delete()
        self.project3.delete()        
        self.user.delete()
        
