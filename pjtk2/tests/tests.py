""" this file contains all of the unit tests assocaited with the
NewProjectForm.  Test include verification of project codes, start
dates, end dates, and year within project code.  Tests of form field
functionality are not included (assumed to be completed by the Django
development team.)"""


from datetime import datetime
from django.contrib.auth.models import User
from django import forms

from pjtk2.models import Project, TL_ProjType, TL_Database
from pjtk2.forms import NewProjectForm
from pjtk2.tests.factories import *

from django.test import TestCase





class TestProjectForm(TestCase):
    
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

        form = NewProjectForm(data=proj, user=UserFactory.build())
        form.full_clean()
        self.assertEqual(form.is_valid(), True)

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

        form = NewProjectForm(data=proj, user=UserFactory.build())
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

        form = NewProjectForm(data=proj, user=UserFactory.build())
        errmsg = "Project end date occurs before start date."
        self.assertIn(errmsg, form.non_field_errors())
        self.assertEqual(form.is_valid(), False)
        

    def test_malformed_prjcd(self):
        """project code does not match required pattern """

        #here are a list of bad, or malformed project codes:
        badcodes = ["LHA_12_103", "LHA_I12D_103", " LH_IS12_103",
                    "LH2_IA12_103", "L00_IA12_103", "LHA_IS12103",
                    "LHA-IS12_103", "LHA_I12D-103", "LHA_IS12_1103",
                    "LHA_IS12A_110", "LHA_IS12_110A" "LHAR_IS12_110"]
        
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
            form = NewProjectForm(data=proj, user=UserFactory.build())
            self.assertIn(errmsg, form.errors['PRJ_CD'])
            self.assertEqual(form.is_valid(), False)

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
            form = NewProjectForm(data=proj, user=UserFactory.build())
            self.assertEqual(form.is_valid(), True)
        

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

        form = NewProjectForm(data=proj, user=UserFactory.build())
        errmsg = "Project start and end date occur in different years."
        self.assertIn(errmsg, form.non_field_errors())
        self.assertEqual(form.is_valid(), False)
