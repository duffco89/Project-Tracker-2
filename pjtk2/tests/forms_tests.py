""" this file contains all of the unit tests assocaited with the
ProjectForm.  Test include verification of project codes, start
dates, end dates, and year within project code.  Tests of form field
functionality are not included (assumed to be completed by the Django
development team.)"""

import os
from StringIO import StringIO
from datetime import datetime

#from django.core.urlresolvers import reverse
from django.test import TestCase
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile

#import unittest

from pjtk2.models import *
from pjtk2.forms import ProjectForm
from pjtk2.forms import ReportUploadForm, ReportUploadFormSet
from pjtk2.tests.factories import *

        
class TestProjectForm(TestCase):

    def setUp(self):
        ProjectFactory.create()
        ##ProjTypeFactory.create()
        ##DatabaseFactory.create()
    
        ##MilestoneFactory.create(label = "Proposal",
        ##                        order = 1)
        ##MilestoneFactory.create(label = "Proposal Presentation",
        ##                        order = 2)
        ##MilestoneFactory.create(label = "Field Protocol Proposal",
        ##                        order = 3)
        ##MilestoneFactory.create(label = "Completion Report",
        ##                        order = 4)
        ##MilestoneFactory.create(label = "Completion Presentation",
        ##                        order = 5)

        
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
        

class TestReportUploadForm(TestCase):

    def generate_file(self):
        try:
            myfile = open('test.csv', 'wb')
            wr = csv.writer(myfile)
            wr.writerow(('Paper ID','Paper Title', 'Authors'))
            wr.writerow(('1','Title1', 'Author1'))
            wr.writerow(('2','Title2', 'Author2'))
            wr.writerow(('3','Title3', 'Author3'))
        finally:
            myfile.close()

        return myfile


    def setUp(self):

        self.rep1 = MilestoneFactory.create(label = "Summary Report",
                                order = 1)
        self.rep2 = MilestoneFactory.create(label = "Proposal Presentation",
                                order = 2)

        self.user = UserFactory(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')

        self.ProjType = ProjTypeFactory()
        
        self.project1 = ProjectFactory.create(PRJ_CD="LHA_IA12_111", YEAR=2012, 
                                              Owner=self.user, slug='lha_ia12_111',
                                              ProjectType = self.ProjType)
        self.project2 = ProjectFactory.create(PRJ_CD="LHA_IA12_222", YEAR=2012, 
                                              Owner=self.user, slug='lha_ia12_222',
                                              ProjectType = self.ProjType)
        self.project3 = ProjectFactory.create(PRJ_CD="LHA_IA12_333", YEAR=2012, 
                                              Owner=self.user, slug='lha_ia12_333',
                                              ProjectType = self.ProjType)

        #NOTE = ProjectReportFactory caused all kinds of grief.
        #Using the real ORM here
        self.projrep = ProjectReports.objects.create(
                       project=self.project1, report_type=self.rep1)

        
        #ProjectReports.objects.create(project=self.project3, report_type=self.rep1)



        #here is fake file that we will upload
        self.mock_file = StringIO('GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
                     '\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        self.mock_file.name = "path/to/some/fake/file.txt"

    def test_submit_reports(self):
        '''submit report and verify that it is associated with that project'''

        #check that we have no completed reports and one outstanding:
        comp = self.project1.get_complete()
        outstanding = self.project1.get_outstanding()
        self.assertEqual(len(comp),0)
        self.assertEqual(len(outstanding),1)

        initial = dict(required=True, report_type = self.rep1, report_path = "")

        #this is the data that is returned from the form:
        data = dict(required=True, report_type = self.rep1)

        file_data = {'report_path': SimpleUploadedFile(self.mock_file.name, 
                                                       self.mock_file.read())}
        form = ReportUploadForm(initial=initial, data=data, project = self.project1,
                                user = self.user, files=file_data)
    
        if form.errors:
            print "form.errors: %s" % form.errors
        if form.non_field_errors():
            print "form.non_field_errors(): %s" % form.non_field_errors()

        self.assertEqual(form.is_valid(), True)

        form.save()
        #verify that this our report is associated with this project
        reports = self.project1.get_reports()
        comp = self.project1.get_complete()
        outstanding = self.project1.get_outstanding()

        self.assertEqual(len(comp),1)
        self.assertEqual(len(outstanding),0)

        self.assertEqual(reports[0].uploaded_by, self.user.username)
        self.assertEqual(str(reports[0].report_path), 
                         os.path.split(self.mock_file.name)[1])
        
        #verify that self.rep2 isnt in the completed list - it isn't done yet:
        projids = [x['report_type_id'] for x in comp.values()] 
        self.assertNotIn(self.rep2.id, projids)


        #and that self.rep1 isnt in the outstanding list - we just did it.
        projids = [x['report_type_id'] for x in outstanding.values()] 
        self.assertNotIn(self.rep1.id, projids)


    def test_upload_with_existing_report(self):
        pass

    def test_upload_sister_projects(self):

        #set up the sister relationship:
        self.project1.add_sister(self.project2.slug)
        #ProjectReports.objects.create(project=self.project2, report_type=self.rep1)
        
        #check that we have no completed reports and one outstanding:
        comp = self.project1.get_complete()
        outstanding = self.project1.get_outstanding()
        self.assertEqual(len(comp),0)
        self.assertEqual(len(outstanding),1)

        initial = dict(required=True, report_type = self.rep1, report_path = "")

        #this is the data that is returned from the form:
        data = dict(required=True, report_type = self.rep1)

        file_data = {'report_path': SimpleUploadedFile(self.mock_file.name, 
                                                       self.mock_file.read())}
        form = ReportUploadForm(initial=initial, data=data, project = self.project1,
                                user = self.user, files=file_data)
    
        self.assertEqual(form.is_valid(), True)

        form.save()

        #THIS PROJECT:
        #verify that this our report is associated with this project
        reports = self.project1.get_reports()
        comp = self.project1.get_complete()
        outstanding = self.project1.get_outstanding()

        self.assertEqual(len(comp),1)
        self.assertEqual(len(outstanding),0)

        self.assertEqual(reports[0].uploaded_by, self.user.username)
        self.assertEqual(str(reports[0].report_path), 
                         os.path.split(self.mock_file.name)[1])
        
        #verify that self.rep2 isnt in the completed list - it isn't done yet:
        projids = [x['report_type_id'] for x in comp.values()] 
        self.assertNotIn(self.rep2.id, projids)


        #and that self.rep1 isnt in the outstanding list - we just did it.
        projids = [x['report_type_id'] for x in outstanding.values()] 
        self.assertNotIn(self.rep1.id, projids)


        #SISTER 1
        #verify that this our report is associated with this project
        reports = self.project2.get_reports()
        comp = self.project2.get_complete()
        outstanding = self.project2.get_outstanding()

        self.assertEqual(len(comp),1)
        self.assertEqual(len(outstanding),0)

        self.assertEqual(reports[0].uploaded_by, self.user.username)
        self.assertEqual(str(reports[0].report_path), 
                         os.path.split(self.mock_file.name)[1])
        
        #verify that self.rep2 isnt in the completed list - it isn't done yet:
        projids = [x['report_type_id'] for x in comp.values()] 
        self.assertNotIn(self.rep2.id, projids)


        #and that self.rep1 isnt in the outstanding list - we just did it.
        projids = [x['report_type_id'] for x in outstanding.values()] 
        self.assertNotIn(self.rep1.id, projids)





    def TearDown(self):
        self.project11.delete()
        self.project12.delete()
        self.project13.delete()
        self.user.delete()
        self.rep1.delete()
        self.rep2.delete()
        self.ProjType.detele()
