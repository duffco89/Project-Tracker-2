from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save, post_save
from django_webtest import WebTest
#from testfixtures import compare
from pjtk2.tests.factories import *
from pjtk2.models import Bookmark

from django.template.defaultfilters import slugify

import datetime
import pytz


def setup():
    '''disconnect the signals before each test - not needed here'''
    pre_save.disconnect(send_notice_prjms_changed, sender=ProjectMilestones)

def teardown():
    '''re-connecct the signals here.'''
    pre_save.disconnect(send_notice_prjms_changed, sender=ProjectMilestones)


class BookmarkTestCase(WebTest):

    def setUp(self):
        ''' '''

        self.user = UserFactory(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')

        self.ProjType = ProjTypeFactory(project_type = "Nearshore Index")

        self.project = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              owner=self.user,
                                              project_type = self.ProjType)
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
        self.assertEqual(bookmark.get_project_code(), self.project.prj_cd)

        #==================
        #  CONFIRM DELETE
        #check that the a get request to unbookmark produce the confirm page
        response = self.app.get(reverse('Unbookmark_Project',
                                args=(self.project.slug,)), user=self.user)
        self.assertEqual(response.status_int, 200)
        self.assertTemplateUsed(response, 'pjtk2/confirm_bookmark_delete.html')

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

        self.ProjType = ProjTypeFactory(project_type = "Nearshore Index")


        self.project1 = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              owner=self.user,
                                              project_type = self.ProjType,
                                              )
        self.project2 = ProjectFactory.create(prj_cd="LHA_IA12_222",
                                              owner=self.user,
                                              project_type = self.ProjType)
        self.project3 = ProjectFactory.create(prj_cd="LHA_IA12_333",
                                              owner=self.user,
                                              project_type = self.ProjType)

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
        #verify that the tag appears as a hyperlink on the details
        #page for this project:
        response = self.app.get(reverse('project_detail',
                                args=(self.project1.slug,)), user=self.user)
        self.assertEqual(response.status_int, 200)

        for tag in tags:
            linkstring= '<a href="%s">%s</a>' % (reverse('TaggedProjects',
                     args=(tag,)), tag)
            self.assertContains(response, linkstring)

        #=======================
        #verify that the tags are NOT associated with project2
        response = self.app.get(reverse('project_detail',
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
        self.assertTemplateUsed(response, 'pjtk2/ProjectForm.html')

        #get the form and submit it
        form = response.form
        form['tags'] = "blue, green, red, yellow"
        response = form.submit()

        print "response = %s" % response


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
        self.assertTemplateUsed('pjtk2/ProjectList.html')

        msg = "<h1>Projects tagged with '%s'</h1>" % tags[0]
        self.assertContains(response, msg, html=True)

        #Project 1
        linkstring= '<a href="%s">%s</a>' % (reverse('project_detail',
                             args = (self.project1.slug,)),
                                             self.project1.prj_cd)
        self.assertContains(response, linkstring, html=True)

        #Project 2
        linkstring= '<a href="%s">%s</a>' % (reverse('project_detail',
                             args = (self.project2.slug,)),
                                             self.project2.prj_cd)
        self.assertContains(response, linkstring, html=True)

        #Project 3
        linkstring= '<a href="%s">%s</a>' % (reverse('project_detail',
                            args = (self.project3.slug,)),
                                             self.project3.prj_cd)
        self.assertNotContains(response, linkstring, html=True)

        #====================
        #navigate to the whole project list and verify that it contain
        #records for all three projects
        response = self.app.get(reverse('ProjectList'), user=self.user)
        self.assertEqual(response.status_int, 200)

        #Project 1
        linkstring= '<a href="%s">%s</a>' % (reverse('project_detail',
                             args = (self.project1.slug,)),
                                             self.project1.prj_cd)
        self.assertContains(response, linkstring, html=True)

        #Project 2
        linkstring= '<a href="%s">%s</a>' % (reverse('project_detail',
                             args = (self.project2.slug,)),
                                             self.project2.prj_cd)
        self.assertContains(response, linkstring, html=True)

        #Project 3
        linkstring= '<a href="%s">%s</a>' % (reverse('project_detail',
                             args = (self.project3.slug,)),
                                             self.project3.prj_cd)
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

        msg =  "Sorry no projects available."
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
                                            category = 'Core', order = 1,
                                            report=True)
        self.rep2 = MilestoneFactory.create(label = "Completion Report",
                                            category = 'Core', order = 2,
                                            report=True)
        self.rep3 = MilestoneFactory.create(label = "Summary Report",
                                            category = 'Core', order = 3,
                                            report=True)
        self.rep4 = MilestoneFactory.create(label = "Budget Report",
                                            category = 'Custom', order = 99,
                                            report=True)
        self.rep5 = MilestoneFactory.create(label = "Creel Summary Statistics",
                                            category = 'Custom', order = 99,
                                            report=True)

        #milestones
        self.ms1 = MilestoneFactory.create(label = "Approved", protected=True,
                                            category = 'Core', order = 1,
                                           report=False)
        self.ms2 = MilestoneFactory.create(label = "Sign off", protected=True,
                                            category = 'Core', order = 999,
                                           report=False)
        self.ms3 = MilestoneFactory.create(label = "Aging", report=False,
                                             category = 'Custom', order = 4)


        #PROJECTS
        self.project1 = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              owner=self.user1)


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
        self.assertTemplateUsed("pjtk2/reportform.html")
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
        self.assertTemplateUsed("pjtk2/reportform.html")
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
        core = self.project1.get_core_assignments(all_reports=False)
        custom = self.project1.get_custom_assignments()
        self.assertEqual(core.count(),2)
        self.assertEqual(custom.count(),1)


    csrf_checks = False
    def test_add_new_report_form(self):
        '''verify that Mr Burns can add a new custom report that is
        not on the original list.'''

        before = Milestone.objects.filter(category='Custom',
                                          report=True).count()
        self.assertEqual(before, 2)

        #Mr Burns navigates to the report update page
        #verify that he can load it
        response = self.app.get(reverse('Reports',
                                args=(self.project1.slug,)),
                                user=self.user2)

        self.assertEqual(response.status_int, 200)
        self.assertTemplateUsed("pjtk2/reportform.html")
        self.assertContains(response, "Core Reporting Requirements")
        self.assertContains(response, "Additional Reporting Requirements")

        #get the sub-report that has the check boxes for reports
        forms = response.forms
        form = forms['dialog']
        form['new_report'] = "COA Summary"
        form.submit()

        #requery the database and verify that the new report has been added:
        after = Milestone.objects.filter(category='Custom', report=True)
        self.assertEqual(after.count(), 3)
        self.assertEqual(after.filter(label="Coa Summary").count(), 1)


    csrf_checks = False
    def test_add_new_milestone_form(self):
        '''verify that Mr Burns can add a new milestone that is
        not on the original list.'''

        before = Milestone.objects.filter(report=False).count()
        #before = self.project1.get_milestones().count()
        self.assertEqual(before, 3)

        #Mr Burns navigates to the report update page
        #verify that he can load it
        response = self.app.get(reverse('Reports',
                                args=(self.project1.slug,)),
                                user=self.user2)

        self.assertEqual(response.status_int, 200)
        self.assertTemplateUsed("pjtk2/reportform.html")
        self.assertContains(response, "Core Reporting Requirements")
        self.assertContains(response, "Additional Reporting Requirements")

        #get the sub-report that has the check boxes for reports
        forms = response.forms
        form = forms['dialog2']
        form['new_milestone'] = "Fieldwork Complete"
        response = form.submit()

        after = Milestone.objects.filter(report=False)
        #after = self.project1.get_milestones()
        self.assertEqual(after.count(), before + 1)
        self.assertEqual(after.filter(label="Fieldwork Complete").count(),1)


    def test_milestones_can_be_changed_from_form(self):
        '''verify that Mr Burns can change the milestone requirements for the
        project - Field work complete isn't needed but Aging Complete
        is
        '''

        #before we submit the report, we want to verify that 'Aging'
        # milestone is not associated with this project
        milestones = self.project1.get_milestones()
        self.assertQuerysetEqual(milestones, ['Approved', 'Sign off'],
                                 lambda a:str(a.milestone.label))

        #Mr Burns navigates to the report update page
        #verify that he can load it
        response = self.app.get(reverse('Reports',
                                args=(self.project1.slug,)),
                                user=self.user2)

        self.assertEqual(response.status_int, 200)
        self.assertTemplateUsed("pjtk2/reportform.html")
        self.assertContains(response, "Project Milestones")

        #get the sub-report that has the check boxes for reports
        forms = response.forms
        #print "forms = %s" % forms

        form = forms['reports']

        form.fields['Milestones'][1].value = 'on'

        form.submit()

        #there should now be three milestones associated with this project
        milestones = self.project1.get_milestones()
        self.assertQuerysetEqual(milestones, ['Approved','Aging','Sign off'],
                                 lambda a:str(a.milestone.label))


    def tearDown(self):

        self.project1.delete()
        self.ms3.delete()
        self.ms2.delete()
        self.ms1.delete()
        self.rep5.delete()
        self.rep4.delete()
        self.rep3.delete()
        self.rep2.delete()
        self.rep1.delete()
        self.user1.delete()
        self.user2.delete()

class MyProjectViewTestCase(WebTest):
    '''Verify that the managers see projecs of their reports in the list
    of 'MyProjects'.  Emplyees will be able to see their projects but
    not their supervisors.  When the supervisors view MyProjects, they
    will have a column 'Project Leader'and will be able to see
    projects of people they supervise.

    '''

    def setUp(self):
        '''create two employees, one supervises the other. Additionally,
        create 3 projects, one run by the supervisor, 2 by the employee.'''

        #self.client = Client()

        self.user = UserFactory(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')

        self.user2 = UserFactory.create(username = 'mburns',
                                first_name = 'Burns',
                                last_name = 'Montgomery',
                                       )

        #mr. burns is an employee without a boss
        self.employee2 = EmployeeFactory(user=self.user2)
        #make mr. burns homer's boss
        self.employee = EmployeeFactory(user=self.user,
                                        supervisor=self.employee2)

        self.ProjType = ProjTypeFactory(project_type = "Nearshore Index")

        #we need approved and sign off milestones
        self.milestone1 = MilestoneFactory.create(label="Approved",
                                             category = 'Core', order=1,
                                             report=False)
        self.milestone2 = MilestoneFactory.create(label="Sign off",
                                        category = 'Core', order=999,
                                             report=False)


        self.project1 = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              prj_ldr=self.user,
                                              owner=self.user,
                                              project_type = self.ProjType)
        self.project2 = ProjectFactory.create(prj_cd="LHA_IA12_222",
                                              prj_ldr=self.user,
                                              owner=self.user,
                                              project_type = self.ProjType)
        #this one is run by mr. burns
        self.project3 = ProjectFactory.create(prj_cd="LHA_IA12_333",
                                              prj_ldr=self.user2,
                                              owner=self.user2,
                                              project_type = self.ProjType)

    def test_employee_version_myprojects(self):

        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('MyProjects'),follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pjtk2/my_projects.html")
        self.assertContains(response, self.project1.prj_cd)
        self.assertContains(response, self.project2.prj_cd)
        #these values should NOT be in the response:
        self.assertNotContains(response, self.project3.prj_cd)
        self.assertNotContains(response, self.user2.username)
        self.assertNotContains(response, "Project Lead")


    def test_supervisor_version_myprojects(self):

        login = self.client.login(username=self.user2.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('MyProjects'),follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pjtk2/my_projects.html")
        self.assertContains(response, self.project1.prj_cd)
        self.assertContains(response, self.project2.prj_cd)

        #these values should be in the response:
        self.assertContains(response, self.project3.prj_cd)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user2.username)
        self.assertContains(response, "Project Lead")


    def test_myprojects_submitted_approved_complete(self):
        '''Verify that projects appear on "My Projects" even if they are
        subitted, approved or completed.
        '''

        self.project1.approve()
        self.project2.approve()
        self.project1.signoff()

        login = self.client.login(username=self.user2.username, password='abc')
        self.assertTrue(login)
        response = self.client.get(reverse('MyProjects'),follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pjtk2/my_projects.html")
        self.assertContains(response, self.project1.prj_cd)
        self.assertContains(response, self.project2.prj_cd)
        self.assertContains(response, self.project3.prj_cd)





    def tearDown(self):
        self.project1.delete()
        self.project2.delete()
        self.project3.delete()
        self.ProjType.delete()
        self.user.delete()
        self.user2.delete()



class TestProjectDetailForm(WebTest):

    def setUp(self):

        #USER
        self.user1 = UserFactory.create(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')

        self.user2 = UserFactory.create(username = 'mburns',
                                first_name = 'Burns',
                                last_name = 'Montgomery',
                                       )

        self.user3 = UserFactory.create(username = 'bgumble',
                                first_name = 'Barney',
                                last_name = 'Gumble',
                                       )


        #make Mr. Burns the manager:
        managerGrp, created = Group.objects.get_or_create(name='manager')
        self.user2.groups.add(managerGrp)

        ##required reports
        #self.rep1 = MilestoneFactory.create(label = "Proposal Presentation",
        #                                    category = 'Core', order = 1,
        #                                    report=True)
        #self.rep2 = MilestoneFactory.create(label = "Completion Report",
        #                                    category = 'Core', order = 2,
        #                                    report=True)
        #self.rep3 = MilestoneFactory.create(label = "Summary Report",
        #                                    category = 'Core', order = 3,
        #                                    report=True)
        #self.rep4 = MilestoneFactory.create(label = "Budget Report",
        #                                    category = 'Custom', order = 99,
        #                                    report=True)
        #self.rep5 = MilestoneFactory.create(label = "Creel Summary Statistics",
        #                                    category = 'Custom', order = 99,
        #                                    report=True)

        #milestones
        self.ms1 = MilestoneFactory.create(label = "Approved", protected=True,
                                           category = 'Core', order = 1,
                                           report=False)

        self.ms2 = MilestoneFactory.create(label = "Fieldwork Complete",
                                           report=False,
                                           category = 'Core', order = 2)

        self.ms3 = MilestoneFactory.create(label = "Data Scrubbed",
                                           report=False,
                                           category = 'Core', order = 3)

        self.ms4 = MilestoneFactory.create(label = "Data Merged", report=False,
                                             category = 'Core', order = 4)

        self.ms5 = MilestoneFactory.create(label = "Sign off", protected=True,
                                            category = 'Core', order = 999,
                                           report=False)

        #PROJECTS
        self.project1 = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              owner=self.user1)




    def test_milestones_render_properly_in_form(self):
        '''verify that the status of the check boxes reflects the status of
        completed field in Project Milestones

        '''

        #first update the 'completed' field for a number of milestones:
        now = datetime.datetime.now(pytz.utc)
        ms = [self.ms1.label, self.ms2.label, self.ms3.label]
        ProjectMilestones.objects.filter(project=self.project1,
                                         milestone__report=False,
                                         milestone__label__in=ms).update(
                                             completed=now)

        milestones = self.project1.get_milestones()
        #a vector of boolean values that indicate status of each milestone
        completed = [x.completed!=None for x in milestones]

        #now homer views the page form:
        login = self.client.login(username=self.user1.username, password='abc')
        self.assertTrue(login)
        response = self.app.get(reverse('EditProject',
                                        args=(self.project1.slug,)),
                                user=self.user1)

        form = response.form
        # grab the values of the check boxes and convert them to
        # another boolean vector
        checked =[x.checked for x in form.fields['milestones']]
        #the status of the check boxes should match the status of the
        #completed field
        self.assertListEqual(completed, checked)


    def test_all_milestones_checked_renders_properly_in_form(self):
        '''Verify that if all milestones are complete, all of the check boxes
        are checked'''

        #first update the 'completed' field for a number of milestones:
        now = datetime.datetime.now(pytz.utc)
        ProjectMilestones.objects.filter(project=self.project1,
                                         milestone__report=False
                                      ).update(completed=now)

        milestones = self.project1.get_milestones()
        #a vector of boolean values that indicate status of each milestone
        completed = [x.completed!=None for x in milestones]

        #now homer views the page form:
        login = self.client.login(username=self.user1.username, password='abc')
        self.assertTrue(login)
        response = self.app.get(reverse('EditProject',
                                        args=(self.project1.slug,)),
                                user=self.user1)

        form = response.form
        # grab the values of the check boxes and convert them to
        # another boolean vector
        checked =[x.checked for x in form.fields['milestones']]
        #the status of the check boxes should match the status of the
        #completed field
        self.assertListEqual(completed, checked)
        #just for giggles:
        check2 = [True] * milestones.count()
        self.assertListEqual(check2, checked)

    def test_status_of_milestones_can_be_updated_by_employee_from_form(self):
        '''verify that Homer can change the milestone requirements for his
        project project - 'Fieldwork complete'.  'Approve' and
        'Sign off' should not be editable for Homer
        '''
        login = self.client.login(username=self.user1.username, password='abc')
        self.assertTrue(login)
        response = self.app.get(reverse('EditProject',
                                        args=(self.project1.slug,)),
                                user=self.user1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pjtk2/ProjectForm.html")
        self.assertContains(response, self.project1.prj_cd)

        form = response.form
        #none of the milestones have been completed yet so none of the
        # check boxes should be checked:
        checked =[x.checked for x in form.fields['milestones']]
        shouldbe = [False] * 5
        self.assertListEqual(checked, shouldbe)

        # Homer says that both field work has been completed and the
        # data scrubbed.
        form.fields['milestones'][1].value = 'on'
        form.fields['milestones'][2].value = 'on'

        response = form.submit().follow()
        #we should be re-directed to to the project detail page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pjtk2/projectdetail.html")
        milestones = self.project1.get_milestones()

        #verify that the milestones homer checked off now have values in
        #completed field:
        shouldbe = [False, True, True, False, False]
        #the lamba function will return True if it has been completed,
        #otherwise false
        self.assertQuerysetEqual(milestones, shouldbe,
                                 lambda a:a.completed!=None)


    def test_status_of_milestones_can_be_updated_by_manager_from_form(self):
        '''verify that Mr Burns can change the update the status of the
        milestone requirements for the project - 'Approved',
        'Fieldwork Complete', and 'Sign Off'
        '''

        #now Mr Burns edits the form
        login = self.client.login(username=self.user2.username, password='abc')
        self.assertTrue(login)
        response = self.app.get(reverse('EditProject',
                                        args=(self.project1.slug,)),
                                user=self.user2)

        form = response.form
        #none of the milestones have been completed yet so none of the
        # check boxes should be checked:
        checked =[x.checked for x in form.fields['milestones']]
        shouldbe = [False] * 5
        self.assertListEqual(checked, shouldbe)

        # Mr Burns says that the project has been approved and that
        # the field work has been completed
        form.fields['milestones'][0].value = 'on'
        form.fields['milestones'][1].value = 'on'

        response = form.submit().follow()
        #we should be re-directed to to the project detail page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pjtk2/projectdetail.html")
        milestones = self.project1.get_milestones()

        #verify that the milestones homer checked off now have values in
        #completed field:
        shouldbe = [True, True, False, False, False]
        #the lamba function will return True if it has been completed,
        #otherwise false
        self.assertQuerysetEqual(milestones, shouldbe,
                                 lambda a:a.completed!=None)

    def test_status_of_milestones_can_be_reversed_from_form(self):
        '''verify that Mr Burns can reverse the status of milestones
        - i.e. milestones that were complete, aren't
        '''
        #first update the 'completed' field for a number of milestones:
        now = datetime.datetime.now(pytz.utc)
        ms = [self.ms1.label, self.ms2.label, self.ms3.label]
        ProjectMilestones.objects.filter(project=self.project1,
                                         milestone__report=False,
                                         milestone__label__in=ms).update(
                                             completed=now)

        milestones = self.project1.get_milestones()

        #verify that the first three milestones are completed
        shouldbe = [True, True, True, False, False]
        #the lamba function will return True if it has been completed,
        #otherwise false
        self.assertQuerysetEqual(milestones, shouldbe,
                                 lambda a:a.completed!=None)

        #now Mr Burns edits the form
        login = self.client.login(username=self.user2.username, password='abc')
        self.assertTrue(login)
        response = self.app.get(reverse('EditProject',
                                        args=(self.project1.slug,)),
                                user=self.user2)
        form = response.form
        #Oops - the field wasn't completed for this project, and the
        #data isn't scrubbed
        form.fields['milestones'][1].value = None
        form.fields['milestones'][2].value = None

        response = form.submit().follow()
        #we should be re-directed to to the project detail page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pjtk2/projectdetail.html")
        milestones = self.project1.get_milestones()

        #verify that the only milestone completed is now the first one
        shouldbe = [True, False, False, False, False]
        #the lamba function will return True if it has been completed,
        #otherwise false
        self.assertQuerysetEqual(milestones, shouldbe,
                                 lambda a:a.completed!=None)



    def test_protected_milestones_are_disabled_for_users(self):
        '''Homer is a project lead, not a manager, and should not be able to
        update protected milestones. Verify that the check boxes
        render with a 'disabled' attribute
        '''
        login = self.client.login(username=self.user1.username, password='abc')
        self.assertTrue(login)
        response = self.app.get(reverse('EditProject',
                                        args=(self.project1.slug,)),
                                user=self.user1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pjtk2/ProjectForm.html")
        self.assertContains(response, self.project1.prj_cd)

        form = response.form

        Enabled = [cb.attrs.get('disabled','enabled') for cb in
                              form.fields['milestones']]
        #verify that the protected milestones are disabled
        shouldbe = ['disabled', 'enabled', 'enabled', 'enabled', 'disabled']

        #the lamba function will return True if it has been completed,
        #otherwise false
        self.assertListEqual(Enabled, shouldbe)



    def test_protected_milestones_are_enabled_for_managers(self):
        '''Mr Burns is a manager, and should be able to
        update protected milestones. Verify that the check boxes
        do NOT render with a 'disabled' attribute
        '''

        login = self.client.login(username=self.user2.username, password='abc')
        self.assertTrue(login)
        response = self.app.get(reverse('EditProject',
                                        args=(self.project1.slug,)),
                                user=self.user2)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pjtk2/ProjectForm.html")
        self.assertContains(response, self.project1.prj_cd)

        form = response.form

        Enabled = [cb.attrs.get('disabled','enabled') for cb in
                                      form.fields['milestones']]

        #verify that the protected milestones are disabled
        shouldbe = ['enabled', 'enabled', 'enabled', 'enabled', 'enabled']

        #the lamba function will return True if it has been completed,
        #otherwise false
        self.assertListEqual(Enabled, shouldbe)


    def test_joeuser_redirected_away_from_project_detail_form(self):
        '''If a user who is not the project owner or a manager tries to access
        the edit form for a project, they should be re-directed to the
        project detail page
        '''

        login = self.client.login(username=self.user3.username, password='abc')
        self.assertTrue(login)
        response = self.app.get(reverse('EditProject',
                                        args=(self.project1.slug,)),
                                user=self.user3).follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pjtk2/projectdetail.html")


    def tearDown(self):
        self.project1.delete()
        self.ms5.delete()
        self.ms4.delete()
        self.ms3.delete()
        self.ms2.delete()
        self.ms1.delete()
        self.user3.delete()
        self.user2.delete()
        self.user1.delete()

class TestCanCopyProject(WebTest):
    '''verify that the project owner, slug and year are correctly
    populated when an existing project is copied using the project crud
    form.'''

    def setUp(self):
        #USER
        self.user1 = UserFactory.create(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')

        self.user2 = UserFactory.create(username = 'bgumble',
                                first_name = 'Barney',
                                last_name = 'Gumble',
                                       )

        self.project1 = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              prj_ldr=self.user1.first_name,
                                              owner=self.user1)


    def test_can_copy_project(self):
        '''verify that we can copy a project with the crud form, that the
        autopopulated fields get filled in appropriately and that the original
        project remains unchanged.'''

        #we want to make sure that none of the attributes of proejct1
        #are changed by making a copy of it
        old_prj_cd = self.project1.prj_cd
        old_prj_ldr = self.project1.prj_ldr
        old_prj_nm = self.project1.prj_nm
        old_owner = self.project1.owner
        old_slug = self.project1.slug
        old_year = self.project1.year

        #barney logs and chooses to copy the existing project
        login = self.client.login(username=self.user2.username, password='abc')
        self.assertTrue(login)
        response = self.app.get(reverse('CopyProject',
                                        args=(self.project1.slug,)),
                                user=self.user2)
        form = response.form

        new_prj_cd = "LHA_IA13_ZZZ"
        new_prj_nm = "Barney's First Project"

        #He needs to fill in a number of the important fields:
        form['prj_cd'] = new_prj_cd
        form['prj_ldr'] = self.user2.first_name
        form['prj_nm'] = new_prj_nm
        #make sure that the project dates match the project code and
        #that date0 happens before date1
        form['prj_date0'] = "2013-6-6"
        form['prj_date1'] = "2013-8-8"

        #if the form is submitted successfully, we should be
        #re-directed to it's details page
        response = form.submit().follow()

        projects = Project.objects.all()
        self.assertEqual(projects.count(),2)

        #check that all of the attributes of the new project have been
        #updated accordingly
        project = Project.objects.get(prj_cd=new_prj_cd)
        #self.assertEqual(project.prj_cd, new_prj_cd)
        self.assertEqual(project.slug, slugify(new_prj_cd))
        self.assertEqual(project.prj_nm, new_prj_nm)
        self.assertEqual(project.prj_ldr, self.user2.first_name)
        self.assertEqual(project.owner, self.user2)
        self.assertEqual(project.year,'2013')

        #now just make sure that the orginial project is unchanged
        #I don't know why it would be.
        project = Project.objects.get(prj_cd=old_prj_cd)
        self.assertEqual(project.slug, slugify(old_prj_cd))
        self.assertEqual(project.prj_nm, old_prj_nm)
        self.assertEqual(project.prj_ldr,old_prj_ldr)
        self.assertEqual(project.owner, old_owner)
        self.assertEqual(project.year, str(old_year))



    def tearDown(self):
        self.project1.delete()
        self.user2.delete()
        self.user1.delete()
