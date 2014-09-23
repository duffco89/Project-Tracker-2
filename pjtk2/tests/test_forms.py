""" this file contains all of the unit tests assocaited with the
ProjectForm.  Test include verification of project codes, start
dates, end dates, and year within project code.  Tests of form field
functionality are not included (assumed to be completed by the Django
development team.)"""

import os
from StringIO import StringIO
from datetime import datetime

#from django.core.urlresolvers import reverse

from django import forms
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from django.core.files.uploadedfile import (SimpleUploadedFile,
                                            InMemoryUploadedFile)
from django.test import TestCase

from pjtk2.models import *
from pjtk2.forms import (ProjectForm, ApproveProjectsForm, SisterProjectsForm,
                         ReportUploadForm, ReportUploadFormSet)
from pjtk2.tests.factories import *


import pytest

@pytest.fixture(scope="module", autouse=True)
def disconnect_signals():
    '''disconnect the signals before each test - not needed here'''
    pre_save.disconnect(send_notice_prjms_changed, sender=ProjectMilestones)



class TestApproveProjectForm(TestCase):

    def setUp(self):

        self.user = UserFactory(username="hsimpson",
                                first_name="Homer", last_name="Simpson")

        self.milestone = MilestoneFactory.create(label="Approved",
                                             category = 'Core', order=1,
                                             report=False)
        self.proj = ProjectFactory.create(prj_cd="LHA_IA12_123",
                                          prj_ldr = self.user,
                                          prj_nm = "Homer's Odyssey")

    def test_ApproveProjectsForm(self):
        '''verify that the same data comes out as went in'''
        initial = dict(
            Approved = self.proj.is_approved(),
            prj_cd = self.proj.prj_cd,
            prj_nm = self.proj.prj_nm,
            prj_ldr = self.proj.prj_ldr,
        )

        form = ApproveProjectsForm(data=initial, instance=self.proj)
        form.is_valid()

        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['prj_cd'],self.proj.prj_cd)
        self.assertEqual(form.cleaned_data['prj_nm'],self.proj.prj_nm)
        self.assertEqual(form.cleaned_data['prj_ldr'],self.proj.prj_ldr)


    def test_ApproveProjectsForm(self):
        '''verify that the data matches the instance data, not the
        original data'''

        initial = dict(
            Approved = False,
            prj_cd = 'ZZZ_ZZ12_ZZZ',
            prj_nm = 'The Wrong Project',
            #prj_ldr = 'George Costanza'
            prj_ldr = self.user.id
        )

        form = ApproveProjectsForm(data=initial, instance=self.proj)
        form.is_valid()

        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.cleaned_data['prj_cd'],self.proj.prj_cd)
        self.assertEqual(form.cleaned_data['prj_nm'],self.proj.prj_nm)
        #self.assertEqual(form.cleaned_data['prj_ldr'],self.proj.prj_ldr)


        #everything but approved should be over-ridden by the instance
        #self.assertEqual(form.cleaned_data['Approved'],initial['Approved'])
        self.assertNotEqual(form.cleaned_data['prj_cd'],initial['prj_cd'])
        self.assertNotEqual(form.cleaned_data['prj_nm'],initial['prj_nm'])
        #self.assertNotEqual(form.cleaned_data['prj_ldr'],initial['prj_ldr'])

    def tearDown(self):
        self.proj.delete()


class TestProjectForm(TestCase):

    def setUp(self):
        ProjectFactory.create()
        self.user = UserFactory(username="hsimpson",
                                first_name="Homer", last_name="Simpson")
        self.dba = DBA_Factory.create()

        self.ptype = ProjTypeFactory()
        self.lake = LakeFactory()
        self.dbase = DatabaseFactory()


    def test_good_data(self):
        """All fields contain valid data """
        proj = dict(
            prj_cd = "LHA_IA12_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = datetime.datetime.strptime("January 15, 2012",
                                                   "%B %d, %Y"),
            prj_date1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),
            comment = "This is a fake project",
            project_type = self.ptype.id,
            master_database = self.dbase.id,
            lake = self.lake.id,
            tags = "red, blue, green",
            owner = self.user.id,
            dba = self.dba.id,
            odoe = 1000,
            salary = 1000
           )

        form = ProjectForm(data=proj)
        form.is_valid()
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
            prj_cd = "LHA_IA12_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = datetime.datetime.strptime("March 15, 2012",
                                                   "%B %d, %Y"),
            prj_date1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),
            comment = "This is a fake project",
            project_type = self.ptype.id,
            master_database = self.dbase.id,
            owner = self.user.id,
            dba = self.dba.id,
            lake=self.lake.id
           )

        for code in goodcodes:
            proj['prj_cd'] = code
            form = ProjectForm(data=proj)
            self.assertEqual(form.is_valid(), True)


    def test_duplicate_project_code(self):
        """Duplicate Project code"""
        proj = dict(
            prj_cd = "LHA_IA12_123",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = datetime.datetime.strptime("January 15, 2012",
                                                   "%B %d, %Y"),
            prj_date1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),
            comment = "This is a fake project",
            project_type = 1,
            master_database = 1,
            owner = self.user.id,
            dba = self.dba.id,
            lake=1
           )

        form = ProjectForm(data=proj)

        errmsg = "Project Code already exists"
        self.assertIn(errmsg, str(form.errors['prj_cd']))
        self.assertEqual(form.is_valid(), False)


    def test_prjcd_too_long(self):
        """project code does not match required pattern """

        #here are a list of bad, or malformed project codes:
        badcodes = ["LHA_IS12A_110", "LHA_IS12_1103","LHAR_IS12_110",
                    "LHA_IS12_110A"]

        proj = dict(
            prj_cd = "LHA_xxx12_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = datetime.datetime.strptime("March 15, 2012",
                                                   "%B %d, %Y"),
            prj_date1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),
            comment = "This is a fake project",
            project_type = 1,
            master_database = 1,
            owner = self.user.id,
            dba = self.dba.id,
            lake=1
           )

        errmsg = "Ensure this value has at most 12 characters"

        for code in badcodes:
            proj['prj_cd'] = code
            form = ProjectForm(data=proj)
            self.assertIn(errmsg, str(form.errors['prj_cd']))
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
            prj_cd = "LHA_12_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = datetime.datetime.strptime("March 15, 2012",
                                                   "%B %d, %Y"),
            prj_date1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),
            comment = "This is a fake project",
            project_type = 1,
            master_database = 1,
            owner = self.user.id,
            dba = self.dba.id,
            lake=1,
           )

        errmsg = "Malformed Project Code."

        for code in badcodes:
            proj['prj_cd'] = code
            form = ProjectForm(data=proj)
            self.assertIn(errmsg, form.errors['prj_cd'])
            self.assertEqual(form.is_valid(), False)


    def test_wrong_year_in_project_code(self):
        """Year on project code does not agree with start and end dates. """

        proj = dict(
            prj_cd = "LHA_IA02_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = datetime.datetime.strptime("January 15, 2012",
                                                   "%B %d, %Y"),
            prj_date1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),
            comment = "This is a fake project",
            project_type = 1,
            master_database = 1,
            owner = self.user.id,
            dba = self.dba.id,
            lake=1
           )

        form = ProjectForm(data=proj)
        errmsg = "Project dates do not agree with project code."
        self.assertIn(errmsg, form.non_field_errors())
        self.assertEqual(form.is_valid(), False)

    def test_end_date_before_start(self):
        """ The end date of the project occures before the start date"""
        proj = dict(
            prj_cd = "LHA_IA12_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = datetime.datetime.strptime("August 15, 2012",
                                                   "%B %d, %Y"),
            prj_date1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),
            comment = "This is a fake project",
            project_type = 1,
            master_database = 1,
            owner = self.user.id,
            dba = self.dba.id,
            lake=1,
           )

        form = ProjectForm(data=proj)
        errmsg = "Project end date occurs before start date."
        self.assertIn(errmsg, form.non_field_errors())
        self.assertEqual(form.is_valid(), False)

    def test_start_end_different_years(self):
        """project start and end date occur in different years """
        proj = dict(
            prj_cd = "LHA_IA12_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = datetime.datetime.strptime("March 15, 2011",
                                                   "%B %d, %Y"),
            prj_date1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),
            comment = "This is a fake project",
            project_type = 1,
            master_database = 1,
            owner = self.user.id,
           )

        form = ProjectForm(data=proj)
        errmsg = "Project start and end date occur in different years."
        self.assertIn(errmsg, form.non_field_errors())
        self.assertEqual(form.is_valid(), False)

    def test_start_date_equal_to_end_date(self):
        """One day project, start date equal to end date. This should be
        allowed and form should be valid."""
        proj = dict(
            prj_cd = "LHA_IA12_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),
            prj_date1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),
            comment = "This is a fake project",
            project_type = self.ptype.id,
            master_database = self.dbase.id,
            owner = self.user.id,
            dba = self.dba.id,
            lake=self.lake.id,
           )

        form = ProjectForm(data=proj)
        if form.errors:
            print "form.errors: %s" % form.errors
        if form.non_field_errors():
            print "form.non_field_errors(): %s" % form.non_field_errors()
        self.assertEqual(form.is_valid(), True)


    def test_date_format(self):
        """The place holder for the project detail form is 'dd/mm/yy'.  This
        test verifies that the date widgets on the form actually accept
        strings in that format."""

        proj = dict(
            prj_cd = "LHA_IA12_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = '15/05/2012',
            prj_date1 = '15/08/2012',
            comment = "This is a fake project",
            project_type = self.ptype.id,
            master_database = self.dbase.id,
            lake = self.lake.id,
            tags = "red, blue, green",
            owner = self.user.id,
            dba = self.dba.id,
           )

        form = ProjectForm(data=proj)
        form.is_valid()
        if form.errors:
            print "form.errors: %s" % form.errors
        if form.non_field_errors():
            print "form.non_field_errors(): %s" % form.non_field_errors()

        self.assertEqual(form.is_valid(), True)


    def test_iso_date_format(self):
        """The place holder for the project detail form is 'yyyy-mm-dd'.  This
        test verifies that the date widgets on the form actually accept
        strings in that format."""

        proj = dict(
            prj_cd = "LHA_IA12_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = '2012-05-15',
            prj_date1 = '2012-08-15',
            comment = "This is a fake project",
            project_type = self.ptype.id,
            master_database = self.dbase.id,
            lake = self.lake.id,
            tags = "red, blue, green",
            owner = self.user.id,
            dba = self.dba.id,
           )

        form = ProjectForm(data=proj)
        form.is_valid()
        if form.errors:
            print "form.errors: %s" % form.errors
        if form.non_field_errors():
            print "form.non_field_errors(): %s" % form.non_field_errors()

        self.assertEqual(form.is_valid(), True)


    def test_inverted_date_formats(self):
        """The place holder for the project detail form is 'dd/mm/yy'.  This
        test verifies that project start and end dates with the month and day
        switched will be caught.
        """

        proj = dict(
            prj_cd = "LHA_IA12_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = '05/15/2012',
            prj_date1 = '08/30/2012',
            comment = "This is a fake project",
            project_type = self.ptype.id,
            master_database = self.dbase.id,
            lake = self.lake.id,
            tags = "red, blue, green",
            owner = self.user.id,
            dba = self.dba.id,
           )

        form = ProjectForm(data=proj)
        errmsg = "Enter a valid date"
        self.assertIn(errmsg, str(form.errors['prj_date0']))
        self.assertIn(errmsg, str(form.errors['prj_date1']))
        self.assertEqual(form.is_valid(), False)

    def test_inverted_iso_date_formats(self):
        """The place holder for the project detail form is 'yyyy-mm-dd'.  This
        test verifies that project start and end dates with the month and day
        switched will be caught.
        """

        proj = dict(
            prj_cd = "LHA_IA12_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = '2012-15-05',
            prj_date1 = '2012-15-08',
            comment = "This is a fake project",
            project_type = self.ptype.id,
            master_database = self.dbase.id,
            lake = self.lake.id,
            tags = "red, blue, green",
            owner = self.user.id,
            dba = self.dba.id,
           )

        form = ProjectForm(data=proj)
        errmsg = "Enter a valid date"
        self.assertIn(errmsg, str(form.errors['prj_date0']))
        self.assertIn(errmsg, str(form.errors['prj_date1']))
        self.assertEqual(form.is_valid(), False)


    def test_bad_odoe_data(self):
        """odoe is not a whole number"""
        proj = dict(
            prj_cd = "LHA_IA12_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = datetime.datetime.strptime("January 15, 2012",
                                                   "%B %d, %Y"),
            prj_date1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),
            comment = "This is a fake project",
            project_type = self.ptype.id,
            master_database = self.dbase.id,
            lake = self.lake.id,
            tags = "red, blue, green",
            owner = self.user.id,
            dba = self.dba.id,
            odoe = 3.14,
            salary = 1000
           )

        form = ProjectForm(data=proj)
        valid = form.is_valid()
        errmsg = "Enter a whole number."
        self.assertIn(errmsg, str(form.errors['odoe']))
        self.assertEqual(valid, False)

    def test_bad_salary_data(self):
        """odoe is not a whole number"""
        proj = dict(
            prj_cd = "LHA_IA12_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = datetime.datetime.strptime("January 15, 2012",
                                                   "%B %d, %Y"),
            prj_date1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),
            comment = "This is a fake project",
            project_type = self.ptype.id,
            master_database = self.dbase.id,
            lake = self.lake.id,
            tags = "red, blue, green",
            owner = self.user.id,
            dba = self.dba.id,
            odoe = 3000,
            salary = 'nice try.'
           )

        form = ProjectForm(data=proj)
        valid = form.is_valid()
        errmsg = "Enter a whole number."
        self.assertIn(errmsg, str(form.errors['salary']))
        self.assertEqual(valid, False)



    def test_Uppercase_Tag_data(self):
        """tags should be automatically converted to lower case. We
        want to make sure that all the projects assocaited with Lake
        Trout include those with 'LAKE TROUT' and 'lake trout'."""

        tags = ["RED", "Blue", "grEEn"]

        proj = dict(
            prj_cd = "LHA_IA12_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = datetime.datetime.strptime("January 15, 2012",
                                                   "%B %d, %Y"),
            prj_date1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),
            comment = "This is a fake project",
            project_type = self.ptype.id,
            master_database = self.dbase.id,
            lake = self.lake.id,
            tags = ', '.join(tags),
            owner = self.user.id,
            dba = self.dba.id,
            odoe = 1000,
            salary = 1000
           )

        form = ProjectForm(data=proj)
        form.is_valid()
        self.assertEqual(form.is_valid(), True)
        #get the tags
        form_tags = form.cleaned_data.get('tags')
        form_tags.sort()
        #make sure that the tags returned are the lower case versions
        #of tags submitted
        should_be = list(set([x.lower() for x in tags]))
        should_be.sort()
        #make sure that the tags returned are the lower case versions
        #of tags submitted
        self.assertEqual(form_tags, should_be)


    def test_Duplicate_Tag_data(self):
        """duplicate tags should be automatically converted to set of lower
        case strings."""

        tags = ["RED", "red", "Blue", "grEEn"]

        proj = dict(
            prj_cd = "LHA_IA12_103",
            prj_nm = "Fake Project",
            prj_ldr = self.user.id,
            prj_date0 = datetime.datetime.strptime("January 15, 2012",
                                                   "%B %d, %Y"),
            prj_date1 = datetime.datetime.strptime("May 15, 2012", "%B %d, %Y"),
            comment = "This is a fake project",
            project_type = self.ptype.id,
            master_database = self.dbase.id,
            lake = self.lake.id,
            tags = ', '.join(tags),
            owner = self.user.id,
            dba = self.dba.id,
            odoe = 1000,
            salary = 1000
           )

        form = ProjectForm(data=proj)
        form.is_valid()
        self.assertEqual(form.is_valid(), True)
        #get the tags
        form_tags = form.cleaned_data.get('tags')
        form_tags.sort()
        #make sure that the tags returned are the lower case versions
        #of tags submitted
        should_be = list(set([x.lower() for x in tags]))
        should_be.sort()

        self.assertItemsEqual(form_tags, should_be)


class TestSelectSistersForm(TestCase):

    def setUp(self):

        #USER
        self.user = UserFactory.create(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')

        #PROJECTS
        self.project1 = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              owner=self.user)
        self.project2 = ProjectFactory.create(prj_cd="LHA_IA12_222",
                                              owner=self.user)
        self.project3 = ProjectFactory.create(prj_cd="LHA_IA12_333",
                                              owner=self.user)

    def test_initial_values(self):
        '''this test will verify that the initial values for project
        code, project name and project leader remain unchanged by the form.'''

        initial = dict(
            prj_cd = 'ZZZ_ZZ12_ZZZ',
            prj_nm = 'The Wrong Project',
            prj_ldr = 'George Costanza'
        )

        data = dict(
            prj_cd = 'YYY_YY12_YYY',
            prj_nm = 'The Second Project',
            prj_ldr = 'Jerry Sienfield'
        )

        form = SisterProjectsForm(initial=initial, data=data)
        form.is_valid()

        #these three fields should be over-ridden by the initial data
        #(they are actually null in the real form - since we used
        #read-only widgets).
        self.assertEqual(form.cleaned_data['prj_cd'],initial['prj_cd'])
        self.assertEqual(form.cleaned_data['prj_nm'],initial['prj_nm'])
        self.assertEqual(form.cleaned_data['prj_ldr'],initial['prj_ldr'])


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
        self.project1 = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              owner=self.user)
        self.project2 = ProjectFactory.create(prj_cd="LHA_IA12_222",
                                              owner=self.user)
        self.project3 = ProjectFactory.create(prj_cd="LHA_IA12_333",
                                              owner=self.user)

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
        form = ReportUploadForm(initial=initial, data=data,
                                project = self.project1,
                                user = self.user, files=file_data)

        if form.errors:
            print "form.errors: %s" % form.errors
        if form.non_field_errors():
            print "form.non_field_errors(): %s" % form.non_field_errors()

        self.assertEqual(form.is_valid(), True)

        form.save()
        #verify that this our report is associated with this project
        reports = self.project1.get_uploaded_reports()
        comp = self.project1.get_complete()
        outstanding = self.project1.get_outstanding()

        self.assertEqual(len(comp),1)
        self.assertEqual(len(outstanding),1)

        self.assertEqual(reports[0].uploaded_by, self.user)

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
        form = ReportUploadForm(initial=initial, data=data,
                                project = self.project1,
                                user = self.user, files=file_data)
        self.assertEqual(form.is_valid(), True)
        form.save()
        #verify that this our report is associated with this project
        reports = self.project1.get_reporting_requirements()
        comp = self.project1.get_complete()
        outstanding = self.project1.get_outstanding()

        self.assertEqual(len(comp),1)
        self.assertEqual(len(outstanding),1)

        #now upload the file 2 to the same project.  It should be
        #associated with the same type of report so this file should
        #replace the first.
        file_data = {'report_path': SimpleUploadedFile(self.mock_file2.name,
                                                       self.mock_file2.read())}
        form = ReportUploadForm(initial=initial, data=data,
                                project = self.project1,
                                user = self.user, files=file_data)
        self.assertEqual(form.is_valid(), True)
        form.save()
        #verify that this our report is associated with this project
        #reports = self.project1.get_reporting_requirements()
        reports = self.project1.get_uploaded_reports()
        comp = self.project1.get_complete()
        outstanding = self.project1.get_outstanding()

        self.assertEqual(len(comp),1)
        self.assertEqual(len(outstanding),1)

        self.assertEqual(reports[0].uploaded_by, self.user)

        filepath = os.path.join(settings.MEDIA_URL,
                                os.path.split(self.mock_file2.name)[1])
        print "filepath = %s" % filepath

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
        form = ReportUploadForm(initial=initial, data=data,
                                project = self.project1,
                                user = self.user, files=file_data)

        self.assertEqual(form.is_valid(), True)

        form.save()

        #THIS PROJECT:
        #verify that this our report is associated with this project
        reports = self.project1.get_uploaded_reports()
        comp = self.project1.get_complete()
        outstanding = self.project1.get_outstanding()

        self.assertEqual(len(comp),1)
        self.assertEqual(len(outstanding),1)

        self.assertEqual(reports[0].uploaded_by, self.user)

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
        reports = self.project2.get_uploaded_reports()
        comp = self.project2.get_complete()
        outstanding = self.project2.get_outstanding()

        self.assertEqual(len(comp),1)
        self.assertEqual(len(outstanding),1)

        self.assertEqual(reports[0].uploaded_by, self.user)

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
