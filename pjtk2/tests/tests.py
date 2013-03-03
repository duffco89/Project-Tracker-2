""" this file contains all of the unit tests assocaited with the
ProjectForm.  Test include verification of project codes, start
dates, end dates, and year within project code.  Tests of form field
functionality are not included (assumed to be completed by the Django
development team.)"""


from datetime import datetime
from django.contrib.auth.models import User
from django import forms

from pjtk2.models import *
from pjtk2.forms import ProjectForm
from pjtk2.tests.factories import *

from django.test import TestCase

import pdb


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

        
        
        
class TestProjectForm(TestCase):

    def setUp(self):
        ProjTypeFactory.create()
        DatabaseFactory.create()
        ProjectFactory.create()
        MilestoneFactory.create(label = "Proposal",
                                order = 1)
        MilestoneFactory.create(label = "Proposal Presentation",
                                order = 2)
        MilestoneFactory.create(label = "Field Protocol Proposal",
                                order = 3)
        MilestoneFactory.create(label = "Completion Report",
                                order = 4)
        MilestoneFactory.create(label = "Completion Presentation",
                                order = 5)

        
    def test_good_data(self):
        """All fields contain valid data """        
        proj = dict(
            PRJ_CD = "LHA_IA12_103",
            PRJ_NM = "Fake Project",
            PRJ_LDR = "Bob Sakamano",
            PRJ_DATE0 = datetime.strptime("January 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            ProjectType = 1,
            MasterDatabase = 1,
            Owner = "Bob Sakamano",
           )

        form = ProjectForm(data=proj)
        if form.errors:
            print "form.errors: %s" % form.errors
        if form.non_field_errors():
            print "form.non_field_errors(): %s" % form.non_field_errors()
            
        self.assertEqual(form.is_valid(), True)


    def test_good_project_codes(self):
        """project codes that should match pattern """

        #here is a list of project codes that should be valid
        #includes codes form research and other lake units
        goodcodes = ["LHS_IA12_103", "LHA_IA12_103", "LHR_IS12_002",
                    "LHA_IA12_XX3", "LHA_IA12_XXX"]
        
        proj = dict(
            PRJ_CD = "LHA_IA12_103",
            PRJ_NM = "Fake Project",
            PRJ_LDR = "Bob Sakamano",
            PRJ_DATE0 = datetime.strptime("March 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            ProjectType = 1,
            MasterDatabase = 1,
            Owner = "Bob Sakamano",
           )

        for code in goodcodes:
            proj['PRJ_CD'] = code
            form = ProjectForm(data=proj)
            self.assertEqual(form.is_valid(), True)

        
    def test_duplicate_project_code(self):
        """Duplicate Project code"""        
        proj = dict(
            PRJ_CD = "LHA_IA12_123",
            PRJ_NM = "Fake Project",
            PRJ_LDR = "Bob Sakamano",
            PRJ_DATE0 = datetime.strptime("January 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            ProjectType = 1,
            MasterDatabase = 1,
            Owner = "Bob Sakamano",
           )

        form = ProjectForm(data=proj)
        #if form.errors:
        #    print "form.errors: %s" % form.errors
        #if form.non_field_errors():
        #    print "form.non_field_errors: %s" % form.non_field_errors()
            
        errmsg = "Project Code already exists"
        self.assertIn(errmsg, str(form.errors['PRJ_CD']))
        self.assertEqual(form.is_valid(), False)





        

    def test_prjcd_too_long(self):
        """project code does not match required pattern """

        #here are a list of bad, or malformed project codes:
        badcodes = ["LHA_IS12A_110", "LHA_IS12_1103","LHAR_IS12_110", "LHA_IS12_110A"]
        
        proj = dict(
            PRJ_CD = "LHA_xxx12_103",
            PRJ_NM = "Fake Project",
            PRJ_LDR = "Bob Sakamano",
            PRJ_DATE0 = datetime.strptime("March 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            ProjectType = 1,
            MasterDatabase = 1,
            Owner = "Bob Sakamano",
           )

        errmsg = "Ensure this value has at most 12 characters"

        for code in badcodes:
            proj['PRJ_CD'] = code
            form = ProjectForm(data=proj)
            self.assertIn(errmsg, str(form.errors['PRJ_CD']))
            self.assertEqual(form.is_valid(), False)


        
        
    def test_malformed_prjcd(self):
        """project code does not match required pattern """

        #here are a list of bad, or malformed project codes:
        badcodes = ["LHA_12_103",   "LHA_I12D_103", " LH_IS12_103",
                    "LH2_IA12_103", "L00_IA12_103", "LHA_IS12103",
                    "LHA-IS12_103", "LHA_I12D-103", "A_IS12_1103",
                    "LHA_IS12_abc", "lha_ID12_103", "LHA_is12_113",                    
                    "LHA_IS1A_110", "LA_IS12_110A", "LH_IS12_110"]
        
        proj = dict(
            PRJ_CD = "LHA_12_103",
            PRJ_NM = "Fake Project",
            PRJ_LDR = "Bob Sakamano",
            PRJ_DATE0 = datetime.strptime("March 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            ProjectType = 1,
            MasterDatabase = 1,
            Owner = "Bob Sakamano",
           )

        errmsg = "Malformed Project Code."

        for code in badcodes:
            proj['PRJ_CD'] = code
            form = ProjectForm(data=proj)
            self.assertIn(errmsg, form.errors['PRJ_CD'])
            self.assertEqual(form.is_valid(), False)

        
    def test_wrong_year_in_project_code(self):
        """Year on project code does not agree with start and end dates. """
        
        proj = dict(
            PRJ_CD = "LHA_IA02_103",
            PRJ_NM = "Fake Project",
            PRJ_LDR = "Bob Sakamano",
            PRJ_DATE0 = datetime.strptime("January 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            ProjectType = 1,
            MasterDatabase = 1,
            Owner = "Bob Sakamano",
           )

        form = ProjectForm(data=proj)
        errmsg = "Project dates do not agree with project code."
        self.assertIn(errmsg, form.non_field_errors())
        self.assertEqual(form.is_valid(), False)

    def test_end_date_before_start(self):
        """ The end date of the project occures before the start date"""
        proj = dict(
            PRJ_CD = "LHA_IA12_103",
            PRJ_NM = "Fake Project",
            PRJ_LDR = "Bob Sakamano",
            PRJ_DATE0 = datetime.strptime("August 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            ProjectType = 1,
            MasterDatabase = 1,
            Owner = "Bob Sakamano",
           )

        form = ProjectForm(data=proj)
        errmsg = "Project end date occurs before start date."
        self.assertIn(errmsg, form.non_field_errors())
        self.assertEqual(form.is_valid(), False)
        
    def test_start_end_different_years(self):
        """project start and end date occur in different years """
        proj = dict(
            PRJ_CD = "LHA_IA12_103",
            PRJ_NM = "Fake Project",
            PRJ_LDR = "Bob Sakamano",
            PRJ_DATE0 = datetime.strptime("March 15, 2011", "%B %d, %Y"),
            PRJ_DATE1 = datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            ProjectType = 1,
            MasterDatabase = 1,
            Owner = "Bob Sakamano",
           )

        form = ProjectForm(data=proj)
        errmsg = "Project start and end date occur in different years."
        self.assertIn(errmsg, form.non_field_errors())
        self.assertEqual(form.is_valid(), False)


    def test_start_date_equal_to_end_date(self):
        """One day project, start date equal to end date. """        
        proj = dict(
            PRJ_CD = "LHA_IA12_103",
            PRJ_NM = "Fake Project",
            PRJ_LDR = "Bob Sakamano",
            PRJ_DATE0 = datetime.strptime("May 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            ProjectType = 1,
            MasterDatabase = 1,
            Owner = "Bob Sakamano",
           )

        form = ProjectForm(data=proj)
        if form.errors:
            print "form.errors: %s" % form.errors
        if form.non_field_errors():
            print "form.non_field_errors(): %s" % form.non_field_errors()
        self.assertEqual(form.is_valid(), True)
        
