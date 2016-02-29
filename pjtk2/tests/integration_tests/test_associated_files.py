'''=============================================================
~/pjtk2/pjtk2/tests/integration_tests/test_associated_files.py
Created: 06 Mar 2014 11:37:43

DESCRIPTION:

tests to verify that associated files are uploaded correctly.  They
should be saved in a project specific directory that contains the
project code.

A. Cottrill
=============================================================

'''


import pytest
from StringIO import StringIO
from django.test import TestCase
from django.conf import settings

from pjtk2.tests.factories import *
from pjtk2.models import AssociatedFile


@pytest.fixture(scope="module", autouse=True)
def disconnect_signals():
    '''disconnect the signals before each test - not needed here'''
    pre_save.disconnect(send_notice_prjms_changed, sender=ProjectMilestones)


#test associated file model:
class TestAssociatedFileModel(TestCase):
    """verify that when we save an associated file, it it's 'upload_to'
    attribute contains the project code of teh project it is
    associated with.

    """
    def setUp(self):
        """
        We need a user and a project.
        Arguments:
        - `self`:
        """

        self.user = UserFactory()
        self.project = ProjectFactory()
        self.project = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                              owner=self.user)

        #here is fake file that we will upload
        self.mock_file0 = StringIO('GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
                     '\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        self.mock_file0.name = "path/to/some/fake/file.txt"

    @pytest.mark.xfail
    def test_associated_file_upload_to(self):
        """

        Arguments:
        - `self`:
      """
        associated_file = AssociatedFile(
            project = self.project,
            file_path = self.mock_file0.name,
            uploaded_by = self.user,
            hash = 'fake hash'
        )

        #associated_file.save()

        print "self.project.prj_cd = %s" % self.project.prj_cd

        print "associated_file.file_path.url = %s" % associated_file.file_path.url
        assert 0==1

    def TearDown(self):
        """

        Arguments:
        - `self`:
        """



class TestActualFileUpload(TestCase):
    ''' These tests use the django test client to upload reports
    associated with different reporting requirements.'''

    def setUp(self):
        #USER
        self.user = UserFactory.create(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')

        self.project = ProjectFactory(prj_cd="LHA_IA12_111",
                                              owner=self.user)

        #here is fake file that we will upload
        self.mock_file0 = StringIO('GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
                     '\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        self.mock_file0.name = "path/to/some/fake/file.txt"

    @pytest.mark.xfail
    def test_upload_single_report(self):
        '''verify that a user can upload a simple file, that the file
        is associated with the correct project and has the correct
        report-type.'''

        self.project.save()

        login = self.client.login(username=self.user.username, password='abc')
        self.assertTrue(login)
        url = reverse('associated_file_upload', args = (self.project.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            'form-0-file_path': self.mock_file0,
            }

        self.client.post(url, form_data)

        #verify that the report was added to the Report table:
        associated_files = AssociatedFile.objects.all()
        self.assertEqual(associated_files.count(), 1)

        filepath = os.path.join('associated_files',
                                self.project.prj_cd,
                                os.path.split(self.mock_file0.name)[1])

        assoc_file = associated_files[0]
        fname = os.path.split(self.mock_file0.name)[1]
        assoc_fname = assoc_file.get_associated_file_upload_path(fname)

        self.assertEqual(filepath, assoc_fname)

        #verify that a link to the file is on the project details page
        url = reverse('project_detail', args = (self.project.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        linkstring= '<a href="%s">%s</a>' % (reverse('serve_file',
                             args = (filepath,)), filepath)

        #print "response = %s" % response

        self.assertContains(response, linkstring)
