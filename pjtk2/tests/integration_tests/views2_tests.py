from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django_webtest import WebTest
#from testfixtures import compare
from pjtk2.tests.factories import *
from pjtk2.models import Bookmark

import datetime


class BookmarkTestCase(WebTest):

    def setUp(self):
        ''' '''
        
        self.user = UserFactory(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')
       
        self.ProjType = ProjTypeFactory(Project_Type = "Nearshore Index")
        
        self.project = ProjectFactory.create(PRJ_CD="LHA_IA12_111", YEAR=2012, 
                                              Owner=self.user, slug='lha_ia12_111',
                                              ProjectType = self.ProjType)
    csrf_checks = False   
    def test_add_delete_bookmarks(self):

        #make sure that we are starting out without any bookmarks
        bookmarkcnt = Bookmark.objects.filter(user__pk=self.user.id).count()
        self.assertEqual(bookmarkcnt, 0)

        #==================
        #   ADD BOOKMARK
        #a request to bookmark should add a bookmark
        response = self.app.get(reverse('Bookmark_Project', 
                                args=(self.project.slug,)), user=self.user)
        self.assertEqual(response.status_int, 302)
        bookmarkcnt = Bookmark.objects.filter(user__pk=self.user.id).count()
        self.assertEqual(bookmarkcnt, 1)
        #make sure the bookmark is the one we think it is:
        bookmark = Bookmark.objects.get(user__pk=self.user.id)
        self.assertEqual(bookmark.get_project_code(), self.project.PRJ_CD)

        #==================
        #  CONFIRM DELETE
        #check that the a get request to unbookmark produce the confirm page
        response = self.app.get(reverse('Unbookmark_Project', 
                                args=(self.project.slug,)), user=self.user)
        self.assertEqual(response.status_int, 200)
        self.assertTemplateUsed(response, 'confirm_bookmark_delete.html')

        #==================
        #  DELETE BOOKMARK
        #check that the post request really does delete the bookmark
        response = self.app.post(reverse('Unbookmark_Project', 
                                args=(self.project.slug,)), user=self.user)
        self.assertEqual(response.status_int, 302)
        bookmarkcnt = Bookmark.objects.filter(user__pk=self.user.id).count()
        self.assertEqual(bookmarkcnt, 0)



class ProjectTaggingTestCase(WebTest):
    '''Verify that the projects can be tagged with keywords in the
    project form.'''

    def setUp(self):
        ''' '''
        
        self.user = UserFactory(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')
       
        self.ProjType = ProjTypeFactory(Project_Type = "Nearshore Index")
        

        self.project1 = ProjectFactory.create(PRJ_CD="LHA_IA12_111",
                                              Owner=self.user,
                                              ProjectType = self.ProjType)
        self.project2 = ProjectFactory.create(PRJ_CD="LHA_IA12_222",
                                              Owner=self.user,
                                              ProjectType = self.ProjType)
        self.project3 = ProjectFactory.create(PRJ_CD="LHA_IA12_333",
                                              Owner=self.user,
                                              ProjectType = self.ProjType)

    def test_tags_in_project_details_view(self):
        '''verify that the tags associated with a project appear on
        its details (and not on others)'''

        #assign some tags to project1
        tags = ['red','blue','green','yellow']
        tags.sort()
        for tag in tags:
            self.project1.tags.add(tag)
            
        #=======================
        #verify that the tags are associated with that project
        tags_back = self.project1.tags.all().order_by("name")
        self.assertQuerysetEqual(tags_back, tags, lambda a:str(a.name))
        self.assertEqual(tags_back.count(),len(tags))
        #verify that the tag appears as a hyperlink on the details page for this project:
        response = self.app.get(reverse('ProjectDetail', 
                                args=(self.project1.slug,)), user=self.user)
        self.assertEqual(response.status_int, 200)

        for tag in tags:
            linkstring= '<a href="%s">%s</a>' % (reverse('TaggedProjects', 
                     args=(tag,)), tag)
            self.assertContains(response, linkstring)

        #=======================
        #verify that the tags are NOT associated with project2
        response = self.app.get(reverse('ProjectDetail', 
                                args=(self.project2.slug,)), user=self.user)
        self.assertEqual(response.status_int, 200)

        for tag in tags:
            linkstring= '<a href="%s">%s</a>' % (reverse('TaggedProjects', 
                     args=(tag,)), tag)
            self.assertNotContains(response, linkstring)


    csrf_checks = False           
    def test_tags_in_project_detail_form(self):
        '''verify that the tags added in project detail form are
        actually associated with the correct project and appear on its
        details page (and not on others)'''

        #call the edit project form for project 1
        response = self.app.get(reverse('EditProject', 
                                args=(self.project1.slug,)), user=self.user)
        self.assertEqual(response.status_int, 200)
        self.assertTemplateUsed(response, 'ProjectForm.html')

        #get the form and submit it
        form = response.form
        form['tags'] = "blue, green, red, yellow"
        form.submit()

        #verify that the tags submitted on the form are actually 
        #saved to the database and associated with this project.
        tags_back = self.project1.tags.all().order_by('name')
        self.assertEqual(tags_back.count(),4)
        self.assertQuerysetEqual(tags_back, ["blue", "green", "red", "yellow"],
                                 lambda a:str(a.name))


    def test_tags_project_list_view(self):

        tags = ['red','blue']
        tags.sort()
        for tag in tags:
            self.project1.tags.add(tag)
            self.project2.tags.add(tag)
            
        #=======================
        #verify that the tags are associated with that project
        tags_back = self.project1.tags.all().order_by("name")
        self.assertQuerysetEqual(tags_back, tags, lambda a:str(a.name))
        tags_back = self.project2.tags.all().order_by("name")
        self.assertQuerysetEqual(tags_back, tags, lambda a:str(a.name))

        #load the page associated with tag 1 and verify that it
        #contains records for projectt 1 and 2 (as hyperlinks), but
        #not project 3
        response = self.app.get(reverse('TaggedProjects', 
                                args=(tags[0],)), user=self.user)
        self.assertEqual(response.status_int, 200)
        self.assertTemplateUsed('ProjectList.html')

        msg = "<h1>Projects tagged with '%s'</h1>" % tags[0]
        self.assertContains(response, msg, html=True)

        #Project 1
        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                             args = (self.project1.slug,)), self.project1.PRJ_CD)
        self.assertContains(response, linkstring, html=True)

        #Project 2
        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                             args = (self.project2.slug,)), self.project2.PRJ_CD)
        self.assertContains(response, linkstring, html=True)

        #Project 3
        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                             args = (self.project3.slug,)), self.project3.PRJ_CD)
        self.assertNotContains(response, linkstring, html=True)

        #====================
        #navigate to the whole project list and verify that it contain
        #records for all three projects
        response = self.app.get(reverse('ProjectList'), user=self.user)
        self.assertEqual(response.status_int, 200)

        #Project 1
        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                             args = (self.project1.slug,)), self.project1.PRJ_CD)
        self.assertContains(response, linkstring, html=True)

        #Project 2
        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                             args = (self.project2.slug,)), self.project2.PRJ_CD)
        self.assertContains(response, linkstring, html=True)

        #Project 3
        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                             args = (self.project3.slug,)), self.project3.PRJ_CD)
        self.assertContains(response, linkstring, html=True)



    def test_tags_project_list_view_tag_doesnot_exist(self):
        '''Verify that the tagged project list will render properly if
        we supply a tag that doesn't exist. A meaningful message
        should be displayed '''

        tags = ['red','blue']
        tags.sort()
        for tag in tags:
            self.project1.tags.add(tag)
            self.project2.tags.add(tag)

        response = self.app.get(reverse('TaggedProjects', 
                                args=("gold",)), user=self.user)
        self.assertEqual(response.status_int, 200)

        msg =  "Sorry no Projects available."
        self.assertContains(response, msg)

    def tearDown(self):
        self.project1.delete()
        self.project2.delete()
        self.project3.delete()
        self.ProjType.delete()
        self.user.delete()


class UpdateReportsTestCase(WebTest):
    '''Verify that we can update the reporting requirements for each
    project through the form.'''

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

        #required reports
        self.rep1 = MilestoneFactory.create(label = "Proposal Presentation",
                                category = 'Core', order = 1)
        self.rep2 = MilestoneFactory.create(label = "Completion Report",
                                category = 'Core', order = 2)
        self.rep3 = MilestoneFactory.create(label = "Summary Report",
                                category = 'Core', order = 3)
        self.rep4 = MilestoneFactory.create(label = "Budget Report",
                                category = 'Custom', order = 99)
        self.rep5 = MilestoneFactory.create(label = "Creel Summary Statistics",
                                category = 'Custom', order = 99)

        #PROJECTS
        self.project1 = ProjectFactory.create(PRJ_CD="LHA_IA12_111", 
                                              Owner=self.user1)


    def test_only_managers_can_view_form(self):
        '''regular user shouldn;t be able to change reporting
        requirements associated with a project - if they try to access
        the url, they will be redirected to the login page'''

        response = self.app.get(reverse('Reports', 
                                args=(self.project1.slug,)), 
                                user=self.user1).follow()

        self.assertEqual(response.status_int, 200)
        self.assertTemplateUsed("auth/login.html")
        self.assertContains(response, "login")
        self.assertContains(response, "password")


    def test_report_form_renders(self):
        '''verify that the report form displays properly with the
        correct number of assignments.  By default all core reports
        should be required.  All custom reports should be listed
        but not checked.'''

        response = self.app.get(reverse('Reports', 
                                args=(self.project1.slug,)), 
                                user=self.user2)

        self.assertEqual(response.status_int, 200)
        self.assertTemplateUsed("reportform.html")
        self.assertContains(response, "Core Reporting Requirements")
        self.assertContains(response, "Additional Reporting Requirements")

        forms = response.forms
        form = forms['reports']

        #there should be three core reports that should be selected:
        self.assertEquals(len(form.fields['Core']), 3)
        self.assertTrue(form.fields['Core'][0].checked)
        self.assertTrue(form.fields['Core'][1].checked)
        self.assertTrue(form.fields['Core'][2].checked)

        #additional reporting requirements - not checked
        self.assertEquals(len(form.fields['Custom']), 2)
        self.assertFalse(form.fields['Custom'][0].checked)
        self.assertFalse(form.fields['Custom'][1].checked)
        


    def test_reports_can_be_updated_from_form(self):
        '''verify that Mr Burns can change the reporting requirements
        for the project - Homer doesn't need to complete a project
        propsal presentation, but he does need to provide a budget
        summary.'''

        #verify that the three core reports and none of the custom
        #reports are assigned before we do anything
        core = self.project1.get_core_assignments()
        custom = self.project1.get_custom_assignments()
        self.assertEqual(core.count(),3)
        self.assertEqual(custom.count(),0)

        #Mr Burns navigates to the report update page
        #verify that he can load it
        response = self.app.get(reverse('Reports', 
                                args=(self.project1.slug,)), 
                                user=self.user2)

        self.assertEqual(response.status_int, 200)
        self.assertTemplateUsed("reportform.html")
        self.assertContains(response, "Core Reporting Requirements")
        self.assertContains(response, "Additional Reporting Requirements")

        #get the sub-report that has the check boxes for reports
        forms = response.forms
        form = forms['reports']

        #turn off one of the core reports and turn on one of the
        #custom reports
        form.fields['Core'][2].value = None
        form.fields['Custom'][1].value = 'on'
        
        form.submit()

        #now there should only be two core reports and one custom
        #report
        core = self.project1.get_core_assignments(all=False)
        custom = self.project1.get_custom_assignments()
        self.assertEqual(core.count(),2)
        self.assertEqual(custom.count(),1)



    ##  NOTE - this test has been replaced with one in views_test.py
    ##  using the django test client.  I was unable to get web test
    ##  to associated data in the second form with 'NewReport' in the
    ##  posted data.
    ##
    csrf_checks = False
    def test_add_new_report_form(self):
        '''verify that Mr Burns can add a new custom report that is
        not on the original list.'''
    
        reports = Milestone.objects.filter(category='Custom')
        self.assertEqual(reports.count(),2)
    
        #Mr Burns navigates to the report update page
        #verify that he can load it
        response = self.app.get(reverse('Reports', 
                                args=(self.project1.slug,)), 
                                user=self.user2)
    
        self.assertEqual(response.status_int, 200)
        self.assertTemplateUsed("reportform.html")
        self.assertContains(response, "Core Reporting Requirements")
        self.assertContains(response, "Additional Reporting Requirements")
    
        #get the sub-report that has the check boxes for reports
        forms = response.forms
        form = forms['dialog']
        form.fields['NewReport'] = "COA Summary"
        
        #form.submit(name='Submit', index=None, get="NewReport")
        form.submit('Submit',{'NewReport':'Submit'})

        
        reports = Milestone.objects.all()
        for rep in reports:
            print rep
    
        #NOTE - these tests currently fail.  I can't figure out how to
        #get webtest to submit second form.
        reports = Milestone.objects.filter(category='Custom')
        #self.assertEqual(reports.count(),3)
        #self.assertEqual(reports.filter(label="COA Summary").count(),1)

    def tearDown(self):

        self.project1.delete()
        self.rep5.delete()
        self.rep4.delete()
        self.rep3.delete()
        self.rep2.delete()
        self.rep1.delete()
        self.user1.delete()
        self.user2.delete()
