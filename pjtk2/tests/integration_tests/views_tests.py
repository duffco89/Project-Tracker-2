import unittest
import pdb


from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase
from django.conf import settings

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

class ApproveUnapproveProjectsTestCase(TestCase):
    '''Verify that a manager can approve and unapprove projects'''

    def setUp(self):
        ''' '''
        #USER
        self.user1 = UserFactory.create(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')

        self.user2 = UserFactory.create(username = 'mburns',
                                first_name = 'Burns',
                                last_name = 'Montgomery',
                                       )
        #make Mr. Burns the manager:
        managerGrp, created = Group.objects.get_or_create(name='manager')         
        self.user2.groups.add(managerGrp)

        #we need to create some models with different years - starting
        #with the current year (the actual model objects use the real
        #current year so the project codes must be dynamically built
        #to ensure the tests pass in the future).
        self.year = datetime.datetime.now().year

        #Two projects from this year:
        PRJ_CD = "LHA_IA%s_111" % str(self.year)[-2:]
        self.project1 = ProjectFactory.create(PRJ_CD=PRJ_CD, Approved=True,
                                              Owner=self.user1)

        PRJ_CD = "LHA_IA%s_222" % str(self.year)[-2:]
        self.project2 = ProjectFactory.create(PRJ_CD=PRJ_CD, Approved=True,
                                              Owner=self.user1)
        #Two projects from last year:
        PRJ_CD = "LHA_IA%s_333" % str(self.year-1)[-2:]
        self.project3 = ProjectFactory.create(PRJ_CD=PRJ_CD, Approved=True,
                                              Owner=self.user1)

        PRJ_CD = "LHA_IA%s_444" % str(self.year-1)[-2:]
        self.project4 = ProjectFactory.create(PRJ_CD=PRJ_CD, Approved=True,
                                              Owner=self.user1)

        #one project from 3 years ago
        PRJ_CD = "LHA_IA%s_555" % str(self.year -3)[-2:]
        self.project5 = ProjectFactory.create(PRJ_CD=PRJ_CD, Approved=True,
                                              Owner=self.user1)

        #One project from next year (submitted by a keener):
        PRJ_CD = "LHA_IA%s_666" % str(self.year+1)[-2:]
        self.project6 = ProjectFactory.create(PRJ_CD=PRJ_CD, Approved=True,
                                              Owner=self.user1)


    def test_without_Login(self):
        '''if we try to view page without logging in, we should be
        re-directed to the login page'''

        response = self.client.get(reverse('ApproveProjects'),
                                   follow=True) 
        self.assertEqual(response.status_code,200)
        redirectstring = "%s?next=%s" % (reverse('login'),
                                         reverse('ApproveProjects'))
        self.assertRedirects(response, redirectstring)



    def test_that_nonmanagers_are_redirected(self):
        '''only managers can approve/unapprove projects.  Verify that
        homer is redirected to the approved project list if he tries
        to log in to the approved projects view.'''


        login = self.client.login(username=self.user1.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('ApproveProjects'), follow=True) 
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed("ApprovedProjectList.html")
        self.assertContains(response, 'Approved Projects')
        self.assertNotContains(response, 'This Year')
        self.assertNotContains(response, 'Last Year')


    def test_that_only_managers_can_login(self):
        '''verify that Mr Burns is able to successful view the form'''
        
        login = self.client.login(username=self.user2.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('ApproveProjects'), follow=True) 
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed("ApproveProjects.html")
        self.assertContains(response, 'This Year')
        self.assertContains(response, 'Last Year')


    def test_that_form_renders_properly(self):
        '''Verify that when Mr. Burns view the form, it contains
        appropriate entries for both this year and last year.  This
        year should contain one entry for a future project year.
        Projects more than one year old should not appear on the form.
        the project codes should also appear as link to their
        respective detail pages.'''


        login = self.client.login(username=self.user2.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('ApproveProjects'), follow=True) 

        print response
        #This year
        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                         args = (self.project1.slug,)), self.project1.PRJ_CD)
        self.assertContains(response, linkstring, html=True)


        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                         args = (self.project2.slug,)), self.project2.PRJ_CD)
        self.assertContains(response, linkstring, html=True)

        #last year

        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                         args = (self.project3.slug,)), self.project3.PRJ_CD)
        self.assertContains(response, linkstring, html=True)

        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                         args = (self.project4.slug,)), self.project4.PRJ_CD)
        self.assertContains(response, linkstring, html=True)

        #the old project should NOT be listed in any form in the response
        self.assertNotContains(response, self.project5.PRJ_CD)
        #the project from the future
        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                         args = (self.project6.slug,)), self.project6.PRJ_CD)
        self.assertContains(response, linkstring, html=True)


    def test_projects_for_thisyear_can_be_approved(self):
        '''by default projects should not be approved.  Verify that
        Mr. Burns can login and successfully approve two from the
        current year.'''

        #by default, the projects are all approved we need to
        #unapproved them before we run this test
        Project.objects.all().update(Approved=False)
        #check that our update worked:
        projects = Project.this_year.all()
        self.assertQuerysetEqual(projects, [False, False, False], lambda a:a.Approved)

        #now login and make the changes
        login = self.client.login(username=self.user2.username, password='abc')
        self.assertTrue(login)

        form_data = {
            'thisyear-TOTAL_FORMS': 3, 
            'thisyear-INITIAL_FORMS': 3,
            'form-type':'thisyear',
            'thisyear-0-id':'6',
            'thisyear-0-Approved': True,
            'thisyear-1-id':'1',
            'thisyear-1-Approved': True,
            'thisyear-2-id':'2',
            'thisyear-2-Approved': True,
            }

        #submit the form
        response = self.client.post(reverse('ApproveProjects'), form_data)

        #they should all be false now:
        thisyear = Project.this_year.all()
        self.assertEqual(thisyear.count(),3)
        self.assertQuerysetEqual(thisyear, [True, True, True], lambda a:a.Approved)

    def test_projects_for_thisyear_can_be_unapproved(self):
        '''Opps - funding was cut.  A project from this year that was
        approved must be unapproved.'''

        login = self.client.login(username=self.user2.username, password='abc')
        self.assertTrue(login)

        #verify database settings before submitting form
        thisyear = Project.this_year.all()
        self.assertEqual(thisyear.count(),3)
        self.assertQuerysetEqual(thisyear, [True, True, True], lambda a:a.Approved)

        form_data = {
            'thisyear-TOTAL_FORMS': 3, 
            'thisyear-INITIAL_FORMS': 3,
            'form-type':'thisyear',
            'thisyear-0-id':'6',
            'thisyear-0-Approved': False,
            'thisyear-1-id':'1',
            'thisyear-1-Approved': False,
            'thisyear-2-id':'2',
            'thisyear-2-Approved': False,
            }

        #submit the form
        response = self.client.post(reverse('ApproveProjects'), form_data)

        #they should all be false now:
        thisyear = Project.this_year.all()
        self.assertEqual(thisyear.count(),3)
        self.assertQuerysetEqual(thisyear, [False, False, False], lambda a:a.Approved)

        #lets make sure that we can submit with both true and false values:
        form_data = {
            'thisyear-TOTAL_FORMS': 3, 
            'thisyear-INITIAL_FORMS': 3,
            'form-type':'thisyear',
            'thisyear-0-id':'6',
            'thisyear-0-Approved': False,
            'thisyear-1-id':'1',
            'thisyear-1-Approved': True,
            'thisyear-2-id':'2',
            'thisyear-2-Approved': False,
            }

        #submit the form
        response = self.client.post(reverse('ApproveProjects'), form_data)

        #they should all be false now:
        thisyear = Project.this_year.all()
        self.assertEqual(thisyear.count(),3)
        self.assertQuerysetEqual(thisyear, [False, True, False], lambda a:a.Approved)


    def test_projects_for_lastyear_can_be_approved(self):
        '''by default projects should not be approved.  Verify that
        Mr. Burns can login and successfully approve a project from last year
        that he forgot to approve then.'''

        #by default, the projects are all approved we need to
        #unapproved them before we run this test
        Project.objects.all().update(Approved=False)
        #check that our update worked:
        projects = Project.last_year.all()
        self.assertQuerysetEqual(projects, [False, False], lambda a:a.Approved)

        login = self.client.login(username=self.user2.username, password='abc')
        self.assertTrue(login)

        #verify database settings before submitting form
        lastyear = Project.last_year.all()
        self.assertEqual(lastyear.count(),2)
        self.assertQuerysetEqual(lastyear, [False, False], lambda a:a.Approved)

        form_data = {
            'lastyear-TOTAL_FORMS': 2, 
            'lastyear-INITIAL_FORMS': 2,
            'form-type':'lastyear',
            'lastyear-0-id':'3',
            'lastyear-0-Approved': True,
            'lastyear-1-id':'4',
            'lastyear-1-Approved': True,
            }

        #submit the form
        response = self.client.post(reverse('ApproveProjects'), form_data)

        #they should all be false now:
        lastyear = Project.last_year.all()
        self.assertEqual(lastyear.count(),2)
        self.assertQuerysetEqual(lastyear, [True, True], lambda a:a.Approved)



    def test_projects_for_lastyear_can_be_unapproved(self):
        '''Verify that Mr. Burns can login and successfully un-approve a
        project from last year that was accidentally approved.'''


        login = self.client.login(username=self.user2.username, password='abc')
        self.assertTrue(login)

        #verify database settings before submitting form
        lastyear = Project.last_year.all()
        self.assertEqual(lastyear.count(),2)
        self.assertQuerysetEqual(lastyear, [True, True], lambda a:a.Approved)

        form_data = {
            'lastyear-TOTAL_FORMS': 2, 
            'lastyear-INITIAL_FORMS': 2,
            'form-type':'lastyear',
            'lastyear-0-id':'3',
            'lastyear-0-Approved': False,
            'lastyear-1-id':'4',
            'lastyear-1-Approved': False,
            }

        #submit the form
        response = self.client.post(reverse('ApproveProjects'), form_data)

        #they should all be false now:
        lastyear = Project.last_year.all()
        self.assertEqual(lastyear.count(),2)
        self.assertQuerysetEqual(lastyear, [False, False], lambda a:a.Approved)

        #lets make sure that we can submit with both true and false values:
        form_data = {
            'lastyear-TOTAL_FORMS': 2, 
            'lastyear-INITIAL_FORMS': 2,
            'form-type':'lastyear',
            'lastyear-0-id':'3',
            'lastyear-0-Approved': False,
            'lastyear-1-id':'4',
            'lastyear-1-Approved': True,
            }

        #submit the form
        response = self.client.post(reverse('ApproveProjects'), form_data)

        #they should all be false now:
        lastyear = Project.last_year.all()
        self.assertEqual(lastyear.count(),2)
        self.assertQuerysetEqual(lastyear, [False, True], lambda a:a.Approved)


    def tearDown(self):

        self.project6.delete()
        self.project5.delete()
        self.project4.delete()
        self.project3.delete()
        self.project2.delete()
        self.project1.delete()
        self.user1.delete()
        self.user2.delete()

class ApproveProjectsEmptyTestCase(TestCase):
    ''' Verify that a meaningful message is displayed if there aren't
    any projects waiting to be approved.'''

    def setUp(self):        

        self.user = UserFactory.create(username = 'mburns',
                                first_name = 'Burns',
                                last_name = 'Montgomery',
                                       )
        #make Mr. Burns the manager:
        managerGrp, created = Group.objects.get_or_create(name='manager')         
        self.user.groups.add(managerGrp)
        self.year = datetime.datetime.now().year
            
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
        self.assertContains(response, 'Approve Projects')
        #this year
        msg = 'There are currently no projects for %s' % self.year
        self.assertContains(response, msg )
        #last year
        msg = 'There are currently no projects for %s' % str(self.year-1)
        self.assertContains(response, msg )

    def tearDown(self):
        self.user.delete()


class ChangeReportingRequirementsTestCase(TestCase):
    '''This class verifies that new reporting requirements can be
    added through the report update form.  This report was originally
    attempted using webtest in views2_test.py.  I was unable to get
    webtest to submit the second "NewReport" form properly.'''

    def setUp(self):        

        #USER
        self.user2 = UserFactory.create(username = 'mburns',
                                first_name = 'Burns',
                                last_name = 'Montgomery',
                                       )
        #make Mr. Burns the manager:
        managerGrp, created = Group.objects.get_or_create(name='manager')         
        self.user2.groups.add(managerGrp)

        self.rep4 = MilestoneFactory.create(label = "Budget Report",
                                category = 'Custom', order = 99)
        self.rep5 = MilestoneFactory.create(label = "Creel Summary Statistics",
                                category = 'Custom', order = 99)

        #PROJECTS
        self.project1 = ProjectFactory.create(PRJ_CD="LHA_IA12_111", 
                                              Owner=self.user2)
            
    def test_Add_New_Report_Type(self):
        '''verify that we can add new report reporting requirements
        using the second from on the UpdateReporting form.'''

        login = self.client.login(username=self.user2.username, password='abc')
        self.assertTrue(login)
        url = reverse('Reports', args=(self.project1.slug,))
        response = self.client.get(url,follow=True) 
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed("reportform.html")
        self.assertContains(response, "Core Reporting Requirements")
        self.assertContains(response, "Additional Reporting Requirements")

        resp = self.client.post(url, {'NewReport': 'COA Summary'})
        self.assertEqual(resp.status_code, 302)

        reports = Milestone.objects.filter(category='Custom')
        self.assertEqual(reports.count(),3)
        self.assertEqual(reports.filter(label="Coa Summary").count(),1)

    def tearDown(self):
       
        self.project1.delete()
        self.rep5.delete()
        self.rep4.delete()
        self.user2.delete()
        


