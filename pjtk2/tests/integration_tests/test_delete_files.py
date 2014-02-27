from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from pjtk2.tests.factories import *

from django.test.client import Client
from django.test import TestCase



class DeleteReportLinkOnDetailPageTestCase(WebTest):
    '''These tests will verify that the delete report button renders on
    project detail appropriately.

    There are alos tests to verify that normal users cannot delete the
    report even if they try to access the url directly and that
    non-logged in users are redirected to a login page..

    '''


    def setUp(self):
        '''In every test, we will need a user, project, a milestone, a
        projectmilestone, and a report.'''

        self.password = "Abcd1234"

        self.user = UserFactory(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson',
                                password=self.password)

        #a required reports
        self.milestone = MilestoneFactory.create(
            label = "Proposal Presentation",
            category = 'Core', order = 1,
            report=True)

        self.project = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              owner=self.user)

        #now we have to associate the report a report with our report
        #milestone.  the m2m relationship makes this a little tricky -
        #can't do it directly in factoryboy.
        #get our projectmilestone:
        self.pmst = self.project.projectmilestones_set.get(
            milestone__label=self.milestone.label)
                              
        #then make a report and associated the pmst with it
        self.report = ReportFactory.create()
        self.report.projectreport.add(self.pmst)
        self.report.save()

        
    def tearDown(self):
        pass

    def test_project_owner_has_delete_link(self):
        '''If the logged user is the project lead, they should be able both
        download the file and delete it.  The project detail should
        contian a link to delete the file.
        '''

        response = self.app.get(reverse('project_detail',
                                args=(self.project.slug,)), user=self.user)
        self.assertEqual(response.status_int, 200)
        
        #our response should contain a link to our file:
        url = reverse('serve_file', kwargs={'filename':self.report.report_path})
        self.assertContains(response, url)                      

        #a link to delete our file
        url = reverse('delete_report', kwargs={'slug':self.project.slug, 
                                               'pk':self.report.id})
        url = '<a href="{0}">'.format(url)
        self.assertContains(response, url)              


    def test_manager_has_delete_link(self):
        '''If a logged in user who is a manager, they should be able both
        download the file and delete it.  The project detail should
        contian a link to delete the file.
        '''

        self.user2 = UserFactory.create(username = 'mburns',
                                first_name = 'Burns',
                                last_name = 'Montgomery',
                                       )
        
        #make Mr. Burns the manager:
        managerGrp, created = Group.objects.get_or_create(name='manager')
        self.user2.groups.add(managerGrp)

        response = self.app.get(reverse('project_detail',
                                        args=(self.project.slug,)), 
                                user=self.user2)
        self.assertEqual(response.status_int, 200)
        
        #our response should contain a link to our file:
        url = reverse('serve_file', kwargs={'filename':self.report.report_path})
        self.assertContains(response, url)                      

        #a link to delete our file
        url = reverse('delete_report', kwargs={'slug':self.project.slug, 
                                               'pk':self.report.id})
        url = '<a href="{0}">'.format(url)
        self.assertContains(response, url)              

        
    def test_admin_has_delete_link(self):

        '''If a logged in user who is an administrator, they should be able both
        download the file and delete it.  The project detail should
        contian a link to delete the file.
        '''

        self.user3 = DBA_Factory.create(username = 'bsimpson',
                                first_name = 'Bart',
                                last_name = 'Simpson',
                                       )
        
        response = self.app.get(reverse('project_detail',
                                        args=(self.project.slug,)), 
                                user=self.user3)
        self.assertEqual(response.status_int, 200)
        
        #our response should contain a link to our file:
        url = reverse('serve_file', kwargs={'filename':self.report.report_path})
        self.assertContains(response, url)                      

        #a link to delete our file
        url = reverse('delete_report', kwargs={'slug':self.project.slug, 
                                               'pk':self.report.id})
        url = '<a href="{0}">'.format(url)
        self.assertContains(response, url)              



    def test_joe_user_does_not_have_delete_link(self):
        '''If a logged in user who is not the project lead or a manager or an
        admin, they should have a link to download the report but not
        delete it.
        '''
        
        self.user4 = UserFactory(username = 'bgumble',
                                first_name = 'Barney',
                                last_name = 'Gumble')

        response = self.app.get(reverse('project_detail',
                                        args=(self.project.slug,)), 
                                user=self.user4)
        self.assertEqual(response.status_int, 200)
        
        #our response should contain a link to our file:
        url = reverse('serve_file', kwargs={'filename':self.report.report_path})
        self.assertContains(response, url)                      

        #a link to delete our file
        url = reverse('delete_report', kwargs={'slug':self.project.slug, 
                                               'pk':self.report.id})
        url = '<a href="{0}">'.format(url)
        self.assertNotContains(response, url)              


    def test_joe_user_cannot_access_delete_report_url(self):
        '''If a logged in user who is not the project lead or a manager or an
        admin, they should be directed back to the project detail
        page if they try to access the delete report url directly.
        '''

        self.user4 = UserFactory(username = 'bgumble',
                                first_name = 'Barney',
                                last_name = 'Gumble')

        response = self.app.get(reverse('delete_report',
                                        kwargs={'slug':self.project.slug,
                                                'pk':self.report.id}), 
                                user=self.user4).follow()

        #make sure that we are successfully redirecte back to the
        #project detail page:
        self.assertEqual(response.status_int, 200)        
        self.assertTemplateUsed('pjtk2/project_detail.html')
        self.assertContains(response, "Project Start:")
        self.assertContains(response, "Project End:")
        self.assertContains(response, "Reporting Requirements:")

 
    def test_anon_user_cannot_access_delete_report_url(self):
        '''If a user is not logged in and try to access the delete report url
        directly, they should be directed back to the login page.
        '''

        response = self.app.get(reverse('delete_report',
                                        kwargs={'slug':self.project.slug,
                                                'pk':self.report.id})).follow()
        #verify that they are re-directed
        self.assertEqual(response.status_int, 301)                
        #url should contain the url to the login (and a bunch of other stuff)
        self.assertIn(reverse('login'),response['Location'])




class DeleteReportTestCase(TestCase):
    '''These tests will verify that project owner, administrator and
    manager can infact delete reports.  Non-owners and non-logged in
    users cannot.

    '''


    def setUp(self):
        '''In every test, we will need a user, project, a milestone, a
        projectmilestone, and a report.'''

        self.password = "Abcd1234"

        self.user = UserFactory(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson',
                                password=self.password)

        #a required reports
        self.milestone = MilestoneFactory.create(
            label = "Proposal Presentation",
            category = 'Core', order = 1,
            report=True)

        self.project = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              owner=self.user)

        #now we have to associate the report a report with our report
        #milestone.  the m2m relationship makes this a little tricky -
        #can't do it directly in factoryboy.
        #get our projectmilestone:
        self.pmst = self.project.projectmilestones_set.get(
            milestone__label=self.milestone.label)
                              
        #then make a report and associated the pmst with it
        self.report = ReportFactory.create()
        self.report.projectreport.add(self.pmst)
        self.report.save()

        
    def tearDown(self):
        pass

    def test_project_owner_can_delete_report_get_get(self):
        '''If the logged user is the project lead, they should be able both
        download the file and delete it.  The project detail should
        contian a link to delete the file.
        '''


        login = self.client.login(username=self.user.username, 
                                  password=self.password)
        self.assertTrue(login)

        response = self.client.get(reverse('delete_report', 
                                           kwargs={'slug':self.project.slug,
                                                   'pk':self.report.id}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('pjtk2/confirm_report_delete.html')


    def test_manager_can_delete_report_get(self):
        '''If a logged in user who is a manager, they should be able both
        download the file and delete it.  The project detail should
        contian a link to delete the file.
        '''

        self.user2 = UserFactory.create(username = 'mburns',
                                        first_name = 'Burns',
                                        last_name = 'Montgomery',
                                        password=self.password)
        
        #make Mr. Burns the manager:
        managerGrp, created = Group.objects.get_or_create(name='manager')
        self.user2.groups.add(managerGrp)

        login = self.client.login(username=self.user2.username, 
                                  password=self.password)
        self.assertTrue(login)

        response = self.client.get(reverse('delete_report', 
                                           kwargs={'slug':self.project.slug,
                                                   'pk':self.report.id}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('pjtk2/confirm_report_delete.html')

        
    def test_admin_can_delete_report_get(self):

        '''If a logged in user who is an administrator, they should be able both
        download the file and delete it.  The project detail should
        contian a link to delete the file.
        '''
 
        self.user3 = DBA_Factory.create(username = 'bsimpson',
                                        first_name = 'Bart',
                                        last_name = 'Simpson',
                                        password = self.password)
        
        login = self.client.login(username=self.user3.username, 
                                   password=self.password)
        print "login = %s" % login
        print "dir(login) = %s" % dir(login)


        self.assertTrue(login)
         
        response = self.client.get(reverse('delete_report', 
                                            kwargs={'slug':self.project.slug,
                                                    'pk':self.report.id}))
         
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('pjtk2/confirm_report_delete.html')
         
 
    def test_joe_user_cannot_delete_report_get(self):
        '''If a logged in user who is not the project lead or a manager or an
        admin, they should have a link to download the report but not
        delete it.
        '''
         
        self.user4 = UserFactory(username = 'bgumble',
                                 first_name = 'Barney',
                                 last_name = 'Gumble',
                                 password = self.password)
        
        login = self.client.login(username=self.user4.username, 
                                  password=self.password)
        self.assertTrue(login)
        
        response = self.client.get(reverse('delete_report', 
                                           kwargs={'slug':self.project.slug,
                                                   'pk':self.report.id}))
        
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('pjtk2/project_detail.html')
         
 


##    def test_joe_user_cannot_access_delete_report_url(self):
##        '''If a logged in user who is not the project lead or a manager or an
##        admin, they should be directed back to the project detail
##        page if they try to access the delete report url directly.
##        '''
##
##        self.user4 = UserFactory(username = 'bgumble',
##                                first_name = 'Barney',
##                                last_name = 'Gumble')
##
##        response = self.app.get(reverse('delete_report',
##                                        kwargs={'slug':self.project.slug,
##                                                'pk':self.report.id}), 
##                                user=self.user4).follow()
##
##        #make sure that we are successfully redirecte back to the
##        #project detail page:
##        self.assertEqual(response.status_int, 200)        
##        self.assertTemplateUsed('pjtk2/project_detail.html')
##        self.assertContains(response, "Project Start:")
##        self.assertContains(response, "Project End:")
##        self.assertContains(response, "Reporting Requirements:")
##
## 
##    def test_anon_user_cannot_access_delete_report_url(self):
##        '''If a user is not logged in and try to access the delete report url
##        directly, they should be directed back to the login page.
##        '''
##
##        response = self.app.get(reverse('delete_report',
##                                        kwargs={'slug':self.project.slug,
##                                                'pk':self.report.id})).follow()
##        #verify that they are re-directed
##        self.assertEqual(response.status_int, 301)                
##        #url should contain the url to the login (and a bunch of other stuff)
##        self.assertIn(reverse('login'),response['Location'])
##
##
