import os
from StringIO import StringIO

from django.core.urlresolvers import reverse
from django_webtest import WebTest
from django.conf import settings

#from testfixtures import compare
from pjtk2.models import ProjectReports
from pjtk2.tests.factories import *

class BasicReportUploadTestCase(WebTest):

    def setUp(self):
        #USER
        self.user = UserFactory.create(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')

        #required reports
        self.rep1 = MilestoneFactory.create(label = "Proposal Presentation",
                                category = 'Core', order = 1)
        self.rep2 = MilestoneFactory.create(label = "Completion Report",
                                category = 'Core', order = 2)
        self.rep3 = MilestoneFactory.create(label = "Summary Report",
                                category = 'Core', order = 3)
        self.rep4 = MilestoneFactory.create(label = "Budget Report",
                                category = 'Custom', order = 99)

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

        self.mock_file3 = StringIO('GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00'
                     '\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        self.mock_file3.name = "path/to/some/fake/file-2.txt"



    def test_render_report_upload_form(self):
        
        url = reverse('ReportUpload', args = (self.project1.slug,))                     
        response = self.app.get(url, user = self.user)

        assert response.status_int == 200
        self.assertTemplateUsed(response, 'UploadReports.html')

        #verify the basic elements of the page
        self.assertIn("Upload Reports", response)
        self.assertIn(self.project1.PRJ_CD, response)
        self.assertIn(self.project1.PRJ_NM, response)

        #each of the core reports should be the response by default: 
        self.assertIn(self.rep1.label, response)
        self.assertIn(self.rep2.label, response)
        self.assertIn(self.rep3.label, response)

        #the fourth report is not core, and has not been assigned to
        #this project.  It should not be in the response:
        self.assertNotIn(self.rep4.label, response)

        form = response.form
        #there should be four forms in the formset
        formcnt = len([x for x in form.fields.keys() if x.endswith("-report_path")])
        self.assertEquals(formcnt,3)



    def test_render_report_upload_form_custom(self):
        '''exactly the same as previous test but with a requirement
        for a custom report'''
        
        self.assertEqual(self.project1.get_assignments().count(),3)
        ProjectReports.objects.create(project=self.project1, 
                                      report_type = self.rep4)
        #verify that this project has 4 reporting requirements now
        self.assertEqual(self.project1.get_assignments().count(),4)

        url = reverse('ReportUpload', args = (self.project1.slug,))                     
        response = self.app.get(url, user = self.user)

        assert response.status_int == 200
        self.assertTemplateUsed(response, 'UploadReports.html')

        #verify the basic elements of the page
        self.assertIn("Upload Reports", response)
        self.assertIn(self.project1.PRJ_CD, response)
        self.assertIn(self.project1.PRJ_NM, response)

        #each of the core reports should be the response by default: 
        self.assertIn(self.rep1.label, response)
        self.assertIn(self.rep2.label, response)
        self.assertIn(self.rep3.label, response)

        #the fourth should now be included in the response
        self.assertIn(self.rep4.label, response)


        form = response.form
        #there should be four forms in the formset
        formcnt = len([x for x in form.fields.keys() if x.endswith("-report_path")])
        self.assertEquals(formcnt, 4)



    def test_upload_report(self):
        '''verify that we can actually upload a file'''

        url = reverse('ReportUpload', args = (self.project1.slug,))                     
        response = self.app.get(url, user = self.user)

        assert response.status_int == 200
        self.assertTemplateUsed(response, 'UploadReports.html')

        #upload mock_file1 to "Proposal Presentation" file field
        form = response.form
        filedata = (self.mock_file.name, self.mock_file.read())
        form.fields['form-0-report_path'][0] = filedata

        #submit the report
        form.submit()        

        report_count = Report.objects.all().count()
        #self.assertEqual(report_count,1)

        #verify that the file name is on the project details page
        url = reverse('ProjectDetail', args = (self.project1.slug,))                     
        response = self.app.get(url, user = self.user)

        #verify that the file name is in queryset returned by  get_reports()
        filepath = os.path.join(settings.MEDIA_URL,
                                os.path.split(self.mock_file.name)[1])
        linkstring= '<a href="%s">%s</a>' % (reverse('serve_file', 
                             args = (filepath,)), filepath)
        #print response
        #self.assertIn(linkstring, response)


    def test_upload_multiple_reports(self):
        '''verify that we can upload more than 1 file'''

        url = reverse('ReportUpload', args = (self.project1.slug,))                     
        response = self.app.get(url, user = self.user)

        assert response.status_int == 200
        self.assertTemplateUsed(response, 'UploadReports.html')

        #upload mock_file1 to "Project Proposal" file field
        #upload mock_file2 to "Summary" file field
        #upload mock_file3 to "Budget Report" file field

        #submit the report 
        #verify that the file names are on the project details page 
        #verify that the file names are associated with the
        #appropriate report type

        #verify that the file names are in queryset returned by  get_reports()


    def test_upload_report_sister_projects(self):
        '''verify that we can upload more than 1 file'''

        url = reverse('ReportUpload', args = (self.project1.slug,))                     
        response = self.app.get(url, user = self.user)

        assert response.status_int == 200
        self.assertTemplateUsed(response, 'UploadReports.html')

        #upload mock_file1 to "Project Proposal" file field
        #submit the report

        #verify that the file name is on the project details page for
        #this project, its sister projecct, but not the third project

        #verify that the file name is in queryset returned by
        #get_reports() for both this project, its sister project but
        #not the thrid project



    def test_upload_multiple_reports_to_sister_projects(self):
        '''verify that we can upload more than 1 file'''

        url = reverse('ReportUpload', args = (self.project1.slug,))                     
        response = self.app.get(url, user = self.user)

        assert response.status_int == 200
        self.assertTemplateUsed(response, 'UploadReports.html')

        #upload mock_file1 to "Project Proposal" file field
        #upload mock_file2 to "Summary" file field
        #upload mock_file3 to "Budget Report" file field


        #submit the report 

        #verify that the file names are on the project details page
        #for project1 and project2, but not project3

        #verify that the file names are associated with the
        #appropriate report types on the details page for this report
        #and its sister

        #verify that the file names are in queryset returned by
        #get_reports() for both this report and its sister







    def tearDown(self):
        self.project1.delete()
        self.project2.delete()
        self.project3.delete()
        self.user.delete()
        self.rep1.delete()
        self.rep2.delete()

        #finally get rid of the temporary file if it was created in
        #this test
        #mock_file1
        filepath = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_URL,
                                os.path.split(self.mock_file.name)[1])
        try:
            os.remove(filepath)          
        except:
            pass

        #mock_file2
        filepath = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_URL,
                                os.path.split(self.mock_file2.name)[1])
        try:
            os.remove(filepath)          
        except:
            pass

        #mock_file3
        filepath = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_URL,
                                os.path.split(self.mock_file3.name)[1])
        try:
            os.remove(filepath)          
        except:
            pass
