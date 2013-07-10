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
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile
from django.conf import settings

#import unittest

from pjtk2.models import *
from pjtk2.forms import (ProjectForm, ApproveProjectsForm, SisterProjectsForm,
                         ReportUploadForm, ReportUploadFormSet)
from pjtk2.tests.factories import *


class TestApproveProjectForm(TestCase):

    def setUp(self):
        self.proj = ProjectFactory.create(PRJ_CD="LHA_IA12_123",
                                          PRJ_LDR = "Homer Simpson",
                                          PRJ_NM = "Homer's Odyssey")
        
    def test_ApproveProjectsForm(self):
        '''verify that the same data comes out as went in'''
        initial = dict(
            Approved = self.proj.Approved,
            PRJ_CD = self.proj.PRJ_CD,
            PRJ_NM = self.proj.PRJ_NM,
            PRJ_LDR = self.proj.PRJ_LDR,
        )

        form = ApproveProjectsForm(data=initial, instance=self.proj)
        form.is_valid()

        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['PRJ_CD'],self.proj.PRJ_CD)
        self.assertEqual(form.cleaned_data['PRJ_NM'],self.proj.PRJ_NM)
        self.assertEqual(form.cleaned_data['PRJ_LDR'],self.proj.PRJ_LDR)


    def test_ApproveProjectsForm(self):
        '''verify that the data matches the instance data, not the
        original data'''

        initial = dict(
            Approved = False,
            PRJ_CD = 'ZZZ_ZZ12_ZZZ',
            PRJ_NM = 'The Wrong Project',
            PRJ_LDR = 'George Costanza'
        )

        form = ApproveProjectsForm(data=initial, instance=self.proj)
        form.is_valid()

        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['PRJ_CD'],self.proj.PRJ_CD)
        self.assertEqual(form.cleaned_data['PRJ_NM'],self.proj.PRJ_NM)
        self.assertEqual(form.cleaned_data['PRJ_LDR'],self.proj.PRJ_LDR)

        #everything but approved should be over-ridden by the instance
        self.assertEqual(form.cleaned_data['Approved'],initial['Approved'])
        self.assertNotEqual(form.cleaned_data['PRJ_CD'],initial['PRJ_CD'])
        self.assertNotEqual(form.cleaned_data['PRJ_NM'],initial['PRJ_NM'])
        self.assertNotEqual(form.cleaned_data['PRJ_LDR'],initial['PRJ_LDR'])


    def tearDown(self):
        self.proj.delete()

        
class TestProjectForm(TestCase):

    def setUp(self):
        ProjectFactory.create()
        self.dba = DBA_Factory.create()
                 

    def test_good_data(self):
        """All fields contain valid data """        
        proj = dict(
            PRJ_CD = "LHA_IA12_103",
            PRJ_NM = "Fake Project",
            PRJ_LDR = "Bob Sakamano",
            PRJ_DATE0 = datetime.datetime.strptime("January 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            project_type = 1,
            master_database = 1,
            Lake =1,
            tags = "red, blue, green",
            Owner = "Bob Sakamano",
            DBA = self.dba.id,
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
            PRJ_DATE0 = datetime.datetime.strptime("March 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            project_type = 1,
            master_database = 1,
            Owner = "Bob Sakamano",
            DBA = self.dba.id,
            Lake=1
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
            PRJ_DATE0 = datetime.datetime.strptime("January 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            project_type = 1,
            master_database = 1,
            Owner = "Bob Sakamano",
            DBA = self.dba.id,
            Lake=1
           )

        form = ProjectForm(data=proj)
            
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
            PRJ_DATE0 = datetime.datetime.strptime("March 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            project_type = 1,
            master_database = 1,
            Owner = "Bob Sakamano",
            DBA = self.dba.id,
            Lake=1
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
            PRJ_DATE0 = datetime.datetime.strptime("March 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            project_type = 1,
            master_database = 1,
            Owner = "Bob Sakamano",
            DBA = self.dba.id,
            Lake=1,
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
            PRJ_DATE0 = datetime.datetime.strptime("January 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            project_type = 1,
            master_database = 1,
            Owner = "Bob Sakamano",
            DBA = self.dba.id,
            Lake=1
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
            PRJ_DATE0 = datetime.datetime.strptime("August 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            project_type = 1,
            master_database = 1,
            Owner = "Bob Sakamano",
            DBA = self.dba.id,
            Lake=1,
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
            PRJ_DATE0 = datetime.datetime.strptime("March 15, 2011", "%B %d, %Y"),
            PRJ_DATE1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            project_type = 1,
            master_database = 1,
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
            PRJ_DATE0 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),
            PRJ_DATE1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),            
            COMMENT = "This is a fake project",
            project_type = 1,
            master_database = 1,
            Owner = "Bob Sakamano",
            DBA = self.dba.id,
            Lake=1,
           )

        form = ProjectForm(data=proj)
        if form.errors:
            print "form.errors: %s" % form.errors
        if form.non_field_errors():
            print "form.non_field_errors(): %s" % form.non_field_errors()
        self.assertEqual(form.is_valid(), True)
        



class TestSelectSistersForm(TestCase):

    def setUp(self):

        #USER
        self.user = UserFactory.create(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')

        #PROJECTS
        self.project1 = ProjectFactory.create(PRJ_CD="LHA_IA12_111", Owner=self.user)
        self.project2 = ProjectFactory.create(PRJ_CD="LHA_IA12_222", Owner=self.user)
        self.project3 = ProjectFactory.create(PRJ_CD="LHA_IA12_333", Owner=self.user)



    def test_initial_values(self):
        '''this test will verify that the initial values for project
        code, project name and project leader remain unchanged by the form.'''

        initial = dict(
            PRJ_CD = 'ZZZ_ZZ12_ZZZ',
            PRJ_NM = 'The Wrong Project',
            PRJ_LDR = 'George Costanza'
        )

        data = dict(
            PRJ_CD = 'YYY_YY12_YYY',
            PRJ_NM = 'The Second Project',
            PRJ_LDR = 'Jerry Sienfield'
        )

        form = SisterProjectsForm(initial=initial, data=data)#, slug=self.project1.slug)
        form.is_valid()

        #these three fields should be over-ridden by the initial data
        #(they are actually null in the real form - since we used read-only widgets).
        self.assertEqual(form.cleaned_data['PRJ_CD'],initial['PRJ_CD'])
        self.assertEqual(form.cleaned_data['PRJ_NM'],initial['PRJ_NM'])
        self.assertEqual(form.cleaned_data['PRJ_LDR'],initial['PRJ_LDR'])



        

    def tearDown(self):
        self.project1.delete()
        self.project2.delete()
        self.project3.delete()
        self.user.delete()


class TestReportUploadForm(TestCase):

    def setUp(self):

        #USER
        self.user = UserFactory.create(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')

        #required reports
        self.rep1 = MilestoneFactory.create(label = "Summary Report",
                                            category = 'Core', order = 1,
                                            report = True)
        self.rep2 = MilestoneFactory.create(label = "Proposal Presentation",
                                            category = 'Core', order = 2,
                                            report = True)

        #PROJECTS
        self.project1 = ProjectFactory.create(PRJ_CD="LHA_IA12_111", Owner=self.user)
        self.project2 = ProjectFactory.create(PRJ_CD="LHA_IA12_222", Owner=self.user)
        self.project3 = ProjectFactory.create(PRJ_CD="LHA_IA12_333", Owner=self.user)

        #here is fake file that we will upload
        self.mock_file = StringIO('GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
                     '\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        self.mock_file.name = "path/to/some/fake/file.txt"

        self.mock_file2 = StringIO('GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
                     '\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        self.mock_file2.name = "path/to/some/fake/file-2.txt"



    def test_submit_reports(self):
        '''submit report and verify that it is associated with that project'''

        #check that we have no completed reports and two outstanding:
        comp = self.project1.get_complete()
        outstanding = self.project1.get_outstanding()
        self.assertEqual(len(comp),0)
        self.assertEqual(len(outstanding),2)

        initial = dict(required=True, milestone = self.rep1, report_path = "")

        #this is the data that is returned from the form:
        data = dict(required=True, milestone = self.rep1)

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
        self.assertEqual(len(outstanding),1)

        self.assertEqual(reports[0].uploaded_by, self.user.username)
        
        filepath = os.path.join(settings.MEDIA_URL,
                                os.path.split(self.mock_file.name)[1])
        self.assertEqual(str(reports[0].report_path), filepath)

        #verify that self.rep2 isnt in the completed list - it isn't done yet:
        projids = [x['milestone_id'] for x in comp.values()] 
        self.assertNotIn(self.rep2.id, projids)

        #and that self.rep1 isnt in the outstanding list - we just did it.
        projids = [x['milestone_id'] for x in outstanding.values()] 
        self.assertNotIn(self.rep1.id, projids)

        #we have uploaded just one report, make sure that's how many
        #records are in Reports
        report_count = Report.objects.all().count()
        self.assertEqual(report_count,1)


    def test_upload_with_existing_report(self):

        #upload report1 to this project (same code as above)
        initial = dict(required=True, milestone = self.rep1, report_path = "")
        data = dict(required=True, milestone = self.rep1)
        file_data = {'report_path': SimpleUploadedFile(self.mock_file.name, 
                                                       self.mock_file.read())}
        form = ReportUploadForm(initial=initial, data=data, project = self.project1,
                                user = self.user, files=file_data)
        self.assertEqual(form.is_valid(), True)
        form.save()
        #verify that this our report is associated with this project
        reports = self.project1.get_reports()
        comp = self.project1.get_complete()
        outstanding = self.project1.get_outstanding()

        self.assertEqual(len(comp),1)
        self.assertEqual(len(outstanding),1)

        #now upload the file 2 to the same project.  It should be
        #associated with the same type of report so this file should
        #replace the first.
        file_data = {'report_path': SimpleUploadedFile(self.mock_file2.name, 
                                                       self.mock_file2.read())}
        form = ReportUploadForm(initial=initial, data=data, project = self.project1,
                                user = self.user, files=file_data)
        self.assertEqual(form.is_valid(), True)
        form.save()
        #verify that this our report is associated with this project
        reports = self.project1.get_reports()
        comp = self.project1.get_complete()
        outstanding = self.project1.get_outstanding()

        self.assertEqual(len(comp),1)
        self.assertEqual(len(outstanding),1)

        self.assertEqual(reports[0].uploaded_by, self.user.username)
        
        filepath = os.path.join(settings.MEDIA_URL,
                                os.path.split(self.mock_file2.name)[1])
        self.assertEqual(str(reports[0].report_path), filepath)


        #we have uploaded two report, make sure that's how many
        #records are in Reports
        report_count = Report.objects.all().count()
        self.assertEqual(report_count,2)


    def test_upload_sister_projects(self):

        #set up the sister relationship:
        self.project1.add_sister(self.project2.slug)
        
        #check that we have no completed reports and one outstanding:
        comp = self.project1.get_complete()
        outstanding = self.project1.get_outstanding()
        self.assertEqual(len(comp),0)
        self.assertEqual(len(outstanding),2)

        initial = dict(required=True, milestone = self.rep1, report_path = "")

        #this is the data that is returned from the form:
        data = dict(required=True, milestone = self.rep1)

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
        self.assertEqual(len(outstanding),1)

        self.assertEqual(reports[0].uploaded_by, self.user.username)

        filepath = os.path.join(settings.MEDIA_URL,
                                os.path.split(self.mock_file.name)[1])
        self.assertEqual(str(reports[0].report_path), filepath)
        
        #verify that self.rep2 isnt in the completed list - it isn't done yet:
        projids = [x['milestone_id'] for x in comp.values()] 
        self.assertNotIn(self.rep2.id, projids)


        #and that self.rep1 isnt in the outstanding list - we just did it.
        projids = [x['milestone_id'] for x in outstanding.values()] 
        self.assertNotIn(self.rep1.id, projids)

        #Project 2
        #this project is a sister so the report we just
        #uploaded should be listed here too verify that this our
        #report is associated with this project
        reports = self.project2.get_reports()
        comp = self.project2.get_complete()
        outstanding = self.project2.get_outstanding()

        self.assertEqual(len(comp),1)
        self.assertEqual(len(outstanding),1)

        self.assertEqual(reports[0].uploaded_by, self.user.username)

        filepath = os.path.join(settings.MEDIA_URL,
                                os.path.split(self.mock_file.name)[1])
        self.assertEqual(str(reports[0].report_path), filepath)

        
        #verify that self.rep2 is not in the completed list - it isn't done yet:
        projids = [x['milestone_id'] for x in comp.values()] 
        self.assertNotIn(self.rep2.id, projids)

        #and that self.rep1 is not in the outstanding list - we just did it.
        projids = [x['milestone_id'] for x in outstanding.values()] 
        self.assertNotIn(self.rep1.id, projids)

        #we have uploaded just one report, make sure that's how many
        #records are in Reports
        report_count = Report.objects.all().count()
        self.assertEqual(report_count,1)


    def tearDown(self):
        self.project1.delete()
        self.project2.delete()
        self.project3.delete()
        self.user.delete()
        self.rep1.delete()
        self.rep2.delete()

        #finally get rid of the temporary file if it was created in
        #this test
        filepath = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_URL,
                                os.path.split(self.mock_file.name)[1])
        try:
            os.remove(filepath)          
        except:
            pass

        filepath = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_URL,
                                os.path.split(self.mock_file2.name)[1])
        try:
            os.remove(filepath)          
        except:
            pass
