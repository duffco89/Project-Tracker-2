'''Some simple tests to verify that my models managers return what
they should'''

from django.test import TestCase
from django.db.models.signals import pre_save, post_save
from pjtk2.models import *
from pjtk2.tests.factories import *

import pytest

@pytest.fixture(scope="module", autouse=True)
def disconnect_signals():
    '''disconnect the signals before each test - not needed here'''
    pre_save.disconnect(send_notice_prjms_changed, sender=ProjectMilestones)

#
#def setup():
#    '''disconnect the signals before each test - not needed here'''
#    pre_save.disconnect(send_notice_prjms_changed, sender=ProjectMilestones)
#
#def teardown():
#    '''re-connecct the signals here.'''
#    pre_save.disconnect(send_notice_prjms_changed, sender=ProjectMilestones)
#

class TestProjectsThisLastYear(TestCase):
    ''''the Project models managers this_year and last_year should only
    return only active project from very specific time periods.  These
    tests verify that this is the case.  Projects.last_year.all() should
    only return projects from one year ago, while this_year should
    return active projects with year is greater than or equal to the
    current year (ensure that projects submitted ahead of time are
    available.).
    '''

    def setUp(self):
        #we need a project lead and a bunch of projects, two from the
        #past, two from last year, two from this year, and two from
        #the future.  Each one of the pair will be inactive and should
        #not be included in the retruned recordsets.
        self.user = UserFactory.create(first_name='Homer',
                                       last_name = 'Simpson',
                                       username = 'hsimpson')

        #tests future proof - we will dynamically create project codes
        yr = datetime.datetime.now()


        # === IN THE PAST ===
        #in the past active
        prj_cd = "LHA_IA%s_111" % str(yr.year - 5)[-2:]
        self.project1 = ProjectFactory.create(prj_cd=prj_cd,
                                              owner = self.user,
                                              active=True)

        #in the pastINactive
        prj_cd = "LHA_IA%s_000" % str(yr.year - 5)[-2:]
        self.project2 = ProjectFactory.create(prj_cd=prj_cd,
                                             owner = self.user,
                                              active=False)

        # === LAST YEAR ===
        #last year active
        prj_cd = "LHA_IA%s_111" % str(yr.year - 1)[-2:]
        self.project3 = ProjectFactory.create(prj_cd=prj_cd,
                                              owner = self.user,
                                              active=True)

        #last year INactive
        prj_cd = "LHA_IA%s_000" % str(yr.year - 1)[-2:]
        self.project4 = ProjectFactory.create(prj_cd=prj_cd,
                                              owner = self.user,
                                              active=False)


        # === THIS YEAR ===
        #this year active
        prj_cd = "LHA_IA%s_111" % str(yr.year)[-2:]
        self.project5 = ProjectFactory.create(prj_cd=prj_cd,
                                              owner = self.user,
                                              active=True)

        #this year INactive
        prj_cd = "LHA_IA%s_000" % str(yr.year)[-2:]
        self.project6 = ProjectFactory.create(prj_cd=prj_cd,
                                              owner = self.user,
                                              active=False)
        # === FUTURE ===
        #next year active
        prj_cd = "LHA_IA%s_111" % str(yr.year + 1)[-2:]
        self.project7 = ProjectFactory.create(prj_cd=prj_cd,
                                              owner = self.user,
                                              active=True)
        #next year INactive
        prj_cd = "LHA_IA%s_000" % str(yr.year + 1)[-2:]
        self.project8 = ProjectFactory.create(prj_cd=prj_cd,
                                              owner = self.user,
                                              active=False)

    def test_active_projects_only(self):
        """By default, the project lists should only include projects where
        active is true - allows us to depreciate projects without deleting
        them from the database."""

        #active projects include project 1,3,5 and 7.
        active = [x.prj_cd for x in [self.project1, self.project3,
                                     self.project5, self.project7]]

        #inactive projects include project 2,4,6, and 8
        inactive = [x.prj_cd for x in [self.project2, self.project4,
                                       self.project6, self.project8]]

        self.assertEqual(self.project1.active, True)
        self.assertEqual(self.project3.active, True)
        self.assertEqual(self.project5.active, True)
        self.assertEqual(self.project7.active, True)

        self.assertEqual(self.project2.active, False)
        self.assertEqual(self.project4.active, False)
        self.assertEqual(self.project6.active, False)
        self.assertEqual(self.project8.active, False)

        projects = Project.objects.all()
        project_codes = [x.prj_cd for x in projects]

        for x in active:
            self.assertIn(x, project_codes)

        for x in inactive:
            self.assertNotIn(x, project_codes)



    def test_projects_lastyear(self):

        #make sure that the project we think exist do
        all_projects = Project.objects.all().count()
        self.assertEqual(all_projects, 4)

        prj_manager = Project.last_year.all()
        #reverse chronological order
        shouldbe = [self.project3.prj_cd]
        self.assertQuerysetEqual(prj_manager, shouldbe,
                                 lambda a:a.prj_cd)

    def test_projects_thisyear(self):

        #make sure that the project we think exist do
        all_projects = Project.objects.all().count()
        self.assertEqual(all_projects, 4)

        prj_manager = Project.this_year.all()
        #reverse chronological order
        shouldbe = [self.project7.prj_cd,self.project5.prj_cd]
        self.assertQuerysetEqual(prj_manager, shouldbe,
                                 lambda a:a.prj_cd)


    def tearDown(self):

        self.project1.delete()
        self.project2.delete()
        self.project3.delete()
        self.project4.delete()
        self.project5.delete()
        self.project6.delete()
        self.project7.delete()
        self.project8.delete()
        self.user.delete()


class TestApprovedCancelledCompletedModelManagers(TestCase):


    def setUp(self):
        '''we will need three projects with easy to rember project codes'''

        self.user = UserFactory(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')

        #Add milestones
        self.milestone1 = MilestoneFactory.create(label="Approved",
                                             category = 'Core', order=1,
                                             report=False)
        self.milestone2 = MilestoneFactory.create(label="Completed",
                                        category = 'Core', order=2,
                                             report=False)
        self.milestone3 = MilestoneFactory.create(label="Sign off",
                                        category = 'Core', order=999,
                                             report=False)


        self.project1 = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              owner=self.user)
        self.project2 = ProjectFactory.create(prj_cd="LHA_IA12_222",
                                              owner=self.user)
        self.project3 = ProjectFactory.create(prj_cd="LHA_IA12_333",
                                              owner=self.user)
        self.project4 = ProjectFactory.create(prj_cd="LHA_IA12_444",
                                              owner=self.user)
        self.project5 = ProjectFactory.create(prj_cd="LHA_IA12_555",
                                              owner=self.user)
        self.project6 = ProjectFactory.create(prj_cd="LHA_IA11_666",
                                              owner=self.user)

        self.project7 = ProjectFactory.create(prj_cd="LHA_IA11_777",
                                              owner=self.user,
                                              cancelled=True)


    def test_ApprovedProjects(self):
        # project 1-4 willb be approved
        self.project1.approve()
        self.project2.approve()
        self.project3.approve()
        self.project4.approve()

        # project 1 and 2 will be signed off
        self.project1.signoff()
        self.project2.signoff()

        #assert approved projects will get 2 projects and that their
        #project codes are the same as self.project3 and self.project4
        approved = Project.objects.approved()
        self.assertEqual(approved.count(),2)
        shouldbe = [self.project3.prj_cd, self.project4.prj_cd]
        self.assertQuerysetEqual(approved, shouldbe, lambda a:a.prj_cd)

        #assert completed projects will get 2 projects and that their
        #project codes are the same as self.project1 and self.project2
        completed = Project.objects.completed()
        self.assertEqual(completed.count(),2)
        shouldbe = [self.project1.prj_cd, self.project2.prj_cd]
        self.assertQuerysetEqual(completed, shouldbe, lambda a:a.prj_cd)


        # projects 5, 6, and 7 have been created but have not been
        # approved or completed, they should be returned by
        #Project.objects.submitted()
        submitted = Project.objects.submitted()
        self.assertEqual(submitted.count(),3)
        shouldbe = [self.project5.prj_cd, self.project6.prj_cd,
                    self.project7.prj_cd]
        self.assertQuerysetEqual(submitted, shouldbe, lambda a:a.prj_cd)


    def test_ApprovedProjects(self):
        '''only one project has cancelled=True, it should be the only one
        returned by project.objects.cancelled'''

        cancelled = Project.objects.cancelled()
        self.assertEqual(cancelled.count(),1)
        shouldbe = [self.project7.prj_cd]
        self.assertQuerysetEqual(cancelled, shouldbe, lambda a:a.prj_cd)


    def tearDown(self):
        self.project1.delete()
        self.project2.delete()
        self.project3.delete()
        self.project4.delete()
        self.project5.delete()
        self.project6.delete()
        self.milestone1.delete()
        self.milestone2.delete()
        self.milestone3.delete()
        self.user.delete()




class TestMilestoneModelManagers(TestCase):
    '''The default milestone mananger has been replaced with one that
    excluded 'Submitted milestones'.  This test verifies that is the
    case.'''

    def setUp(self):
        '''we will need three projects with easy to rember project codes'''

        self.user = UserFactory(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')

        self.employee = EmployeeFactory(user=self.user)

        #Add milestones
        self.milestone0 = MilestoneFactory.create(label="Submitted",
                                             category = 'Core', order=1,
                                             report=False)
        self.milestone1 = MilestoneFactory.create(label="Approved",
                                                  shared=True,
                                                  category = 'Core', order=2,
                                                  report=False)
        self.milestone2 = MilestoneFactory.create(label="Completed",
                                                  shared=True,
                                                  category = 'Core', order=3,
                                                  report=False)
        self.milestone3 = MilestoneFactory.create(label="Sign off",
                                        category = 'Core', order=999,
                                             report=False)
        #create a project
        self.project1 = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              owner=self.user)


    def test_ApprovedProjects(self):
        '''The default manager shoul now exclude 'Submitted'.  Submitted is
        available through Milestones.allmilestones.all()'''

        all_milestones = [self.milestone0.label, self.milestone1.label,
                          self.milestone2.label, self.milestone3.label]
        #this one should NOT include 'Submitted'
        qs = Milestone.objects.all()
        self.assertQuerysetEqual(qs, all_milestones[1:],
                                 lambda a:a.label)

        #this one should include 'Submitted'
        qs = Milestone.allmilestones.all()
        self.assertQuerysetEqual(qs, all_milestones,
                                 lambda a:a.label)


    def test_SharedMilestones(self):
        '''the milestone manager has a shared() method.  This test verifies that
        only shared Milestone are returned by Milestone.objects.shared()'''

        #get the shared milestones
        shared = Milestone.objects.shared()
        #we should only have the two that we created with 'shared=True'
        shouldbe = [self.milestone1.label, self.milestone2.label,]

        self.assertQuerysetEqual(shared, shouldbe, lambda a:a.label)

    def tearDown(self):
        self.project1.delete()
        self.milestone0.delete()
        self.milestone1.delete()
        self.milestone2.delete()
        self.milestone3.delete()
        self.employee.delete()
        self.user.delete()



class TestMessageModelManagers(TestCase):
    '''Only messages associated with active projects should be returned by
    the message and messages2users managers
    '''

    def setUp(self):
        '''we will need two projects - one will be active, one will be in
        active.  Only one milestone is needed.'''


        self.user = UserFactory.create(first_name='Homer',
                                       last_name = 'Simpson',
                                       username = 'hsimpson')

        self.employee = EmployeeFactory(user=self.user)

        self.milestone = MilestoneFactory.create(label="Submitted",
                                             category = 'Core', order=1,
                                             report=False)

        self.project1 = ProjectFactory.create(prj_cd = "LHA_IA12_123",
                                              owner = self.user,
                                              active=True)

        self.project2 = ProjectFactory.create(prj_cd = "LHA_IA12_999",
                                              owner = self.user,
                                              active=False)


    def test_message_manager(self):
        '''There should only be one message returned by the messages manager -
        the submitted message for project 1'''

        msgs = Message.objects.all()

        self.assertEqual(msgs.count(),1)
        self.assertEqual(msgs[0].project_milestone.milestone, self.milestone)
        self.assertEqual(msgs[0].project_milestone.project, self.project1)


    def test_messages2users_manager(self):
        '''the messages2 users should only return messages associated
        with the first (active) project, the second (inactive) project
        should not be returned.'''

        msgs2users = Messages2Users.objects.all()

        prj_cds = [x.message.project_milestone.project.prj_cd for x in
                  msgs2users]

        self.assertIn(self.project1.prj_cd, prj_cds)
        self.assertNotIn(self.project2.prj_cd, prj_cds)


    def tearDown(self):
        self.project1.delete()
        self.project2.delete()
        self.milestone.delete()
        self.user.delete()
