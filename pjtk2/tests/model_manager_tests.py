'''Some simple tests to verify that my models managers return what
they should'''

from django.test import TestCase
from django.db.models.signals import pre_save, post_save
from pjtk2.models import *
from pjtk2.tests.factories import *


def setup():
    '''disconnect the signals before each test - not needed here'''
    pre_save.disconnect(send_notice_prjms_changed, sender=ProjectMilestones)

def teardown():
    '''re-connecct the signals here.'''
    pre_save.disconnect(send_notice_prjms_changed, sender=ProjectMilestones)


class TestProjectsThisLastYear(TestCase):
    ''''the Project models manaagers this_year and last_year should only
    return only active project from very specific time periods.  These
    tests verify that is the case.  Projects.last_year.all() should
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


    def test_projects_lastyear(self):

        #make sure that the project we think exist do
        all_projects = Project.objects.all().count()
        self.assertEqual(all_projects,8)

        prj_manager = Project.last_year.all()
        #reverse chronological order
        shouldbe = [self.project3.prj_cd]
        self.assertQuerysetEqual(prj_manager, shouldbe,
                                 lambda a:a.prj_cd)

    def test_projects_thisyear(self):

        #make sure that the project we think exist do
        all_projects = Project.objects.all().count()
        self.assertEqual(all_projects,8)

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


class TestApprovedCompletedModelManagers(TestCase):
    

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


        # projects 5 and 6 have been created but have not been
        # approved or completed, they should be returned by 
        #Project.objects.submitted()
        submitted = Project.objects.submitted()
        self.assertEqual(submitted.count(),2)
        shouldbe = [self.project5.prj_cd, self.project6.prj_cd]
        self.assertQuerysetEqual(submitted, shouldbe, lambda a:a.prj_cd)

            
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
                                             category = 'Core', order=2, 
                                             report=False)
        self.milestone2 = MilestoneFactory.create(label="Completed",
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
            
    def tearDown(self):
        self.project1.delete()
        self.milestone0.delete()
        self.milestone1.delete()
        self.milestone2.delete()
        self.milestone3.delete()
        self.employee.delete()
        self.user.delete()

