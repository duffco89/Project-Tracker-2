from django.test import TestCase

from pjtk2.models import *
from pjtk2.tests.factories import *

class TestProjectModel(TestCase):

    def setUp(self):
        ProjTypeFactory.build()
        DatabaseFactory.build()        
        ProjectFactory.build()


    def test_resetMilestone(self):
        '''reset milestones is a method that is used to clear all of the
        milestones associated with a project.  used when we create new
        projects by copying old ones.  we don't want to include the old
        milestones in the new project'''
        
        project = ProjectFactory.create()
        #project = Project.objects.get(pk=1)

        #pdb.set_trace()
        #the default for all of these milestones should be False
        self.assertEqual(project.Approved, False)
        self.assertEqual(project.Conducted, False)
        self.assertEqual(project.DataScrubbed, False)                
        self.assertEqual(project.DataMerged, False)
        self.assertEqual(project.SignOff, False)                

        #reset them all to true
        project.Approved = True
        project.Conducted = True
        project.DataScrubbed = True
        project.DataMerged = True
        project.SignOff = True

        #verity that they have all been changed
        self.assertEqual(project.Approved, True)
        self.assertEqual(project.Conducted, True)
        self.assertEqual(project.DataScrubbed, True)                
        self.assertEqual(project.DataMerged, True)
        self.assertEqual(project.SignOff, True)                

        #run our reset method
        project.resetMilestones()

        #verify that each of the milestones are infact False
        self.assertEqual(project.Approved, False)
        self.assertEqual(project.Conducted, False)
        self.assertEqual(project.DataScrubbed, False)                
        self.assertEqual(project.DataMerged, False)
        self.assertEqual(project.SignOff, False)                


    def test_project_unicode(self):
        """make sure that the string representation of our project is
        what we expect (project name (project code))"""
        prj_cd = "LHA_IA12_111"
        prj_nm = "Fake Project"
        project = ProjectFactory.create(PRJ_CD = prj_cd,
                                        PRJ_NM = prj_nm)
        should_be = "%s (%s)" % (prj_nm, prj_cd)
        self.assertEqual(str(project), should_be)                


    def test_project_suffix(self):
        '''verify that project suffix is the last three elements of
        the project code'''
        prj_cd = "LHA_IA12_111"
        prj_nm = "Fake Project"
        project = ProjectFactory.create(PRJ_CD = prj_cd,
                                        PRJ_NM = prj_nm)
        self.assertEqual(len(project.ProjectSuffix()), 3)                
        should_be = prj_cd[-3:]
        self.assertEqual(project.ProjectSuffix(), should_be)                


    def test_project_save(self):
        '''verify that the fields populated on save are what they
        should be'''
        prj_cd = "LHA_IA12_111"
        prj_nm = "Fake Project"
        project = ProjectFactory.create(PRJ_CD = prj_cd)

        project.save()
        should_be = prj_cd.lower()
        self.assertEqual(project.slug, should_be)
        should_be = "20" + prj_cd[6:8]                
        self.assertEqual(str(project.YEAR), should_be)                

class TestMilestoneModel(TestCase):        

    def setUp(self):

        core1 = MilestoneFactory.create(label="core1",
                                        category = 'Core', order=1)
        core2 = MilestoneFactory.create(label="core2",
                                        category = 'Core', order=2)
        core3 = MilestoneFactory.create(label="core3",
                                        category = 'Core', order=3)
        self.project = ProjectFactory.create()


    def test_initial_reports_on_save_method(self):
        # make some fake reports, the three core reports should be
        # automatically associated with a new project, and verify that
        # the custom report is not when the project is created.
                
        myreports = ProjectReports.objects.filter(project=self.project)
        self.assertEqual(myreports.count(), 3)

    def test_get_assigment_methods(self):
        
        self.assertEqual(self.project.get_assignments().count(), 3)
        self.assertNotEqual(self.project.get_assignments().count(), 2)
        self.assertNotEqual(self.project.get_assignments().count(), 4)
        
        self.assertEqual(self.project.get_core_assignments().count(), 3)
        self.assertEqual(self.project.get_custom_assignments().count(), 0)
        
        #we haven't uploaded any reports, so this should be 0
        self.assertEqual(self.project.get_complete().count(), 0)

    def test_get_assigment_methods_w_custom_report(self): 

        '''verify that custom reports are can be added and retrieved
        as expected.'''

        custom1 = MilestoneFactory.create(label="custom1", 
                                          category = 'Custom', order=99)

        projectreport = ProjectReportsFactory(project=self.project,
                                             report_type=custom1)
        
        self.assertEqual(self.project.get_assignments().count(), 4)
        self.assertNotEqual(self.project.get_assignments().count(), 3)
        self.assertNotEqual(self.project.get_assignments().count(), 5)
        
        self.assertEqual(self.project.get_core_assignments().count(), 3)
        self.assertEqual(self.project.get_custom_assignments().count(), 1)

        report = self.project.get_custom_assignments()[0]
        self.assertEqual(report.required, True)
        self.assertEqual(str(report.report_type), 'custom1')
        
        #we haven't uploaded any reports, so this should be 0
        self.assertEqual(self.project.get_complete().count(), 0)

        
        
class TestModelReports(TestCase):        

    def setUp(self):

        core1 = MilestoneFactory.create(label="core1",
                                        category = 'Core', order=1)
        self.project = ProjectFactory.create()

        #retrieve the projectreport that would have been created for
        #the new project
        self.projectreport = ProjectReports.objects.get(project=self.project,
                                                   report_type=core1)

        #create a fake report
        report = ReportFactory(report_path="path\to\fake\file.txt")
        #associate the report with the project reporting requirement
        report.projectreport.add(self.projectreport) 
        
    def test_get_reports(self):
        rep = self.project.get_reports()
        self.assertEqual(len(rep),1)
        self.assertEqual(rep[0].report_path, "path\to\fake\file.txt")
        #self.fail("Finish this test.")

        
        
        
        
