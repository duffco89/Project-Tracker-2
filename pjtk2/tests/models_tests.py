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
