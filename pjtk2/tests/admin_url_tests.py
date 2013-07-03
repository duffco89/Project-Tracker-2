'''Some simple tests to quickly verify that all of the urls work and
that the admin contains interfaces to the models that we need.'''

from pjtk2.tests import DemoTestCase
from django.core.urlresolvers import reverse
from pjtk2.tests.factories import *


class TestUrls(DemoTestCase):

    def setUp(self):

        #PROJECT
        self.project = ProjectFactory.create(PRJ_CD="LHA_IA12_111")

    def test_urls(self):
        '''Verify that all of the pages exist.  Can't use template_used
        because all views require login.  They are re-directed to the
        login'''
        URLS = (

            (reverse('login'),
             {'status_code':200}),

            (reverse('logout'),
             {'status_code':302}),

            (reverse('ProjectList'),
             {'status_code': 302}),

            (reverse('NewProject'),
             {'status_code': 302}),
            
            (reverse('CopyProject', args=(self.project.slug,)),
             {'status_code': 302}),
            
            (reverse('EditProject', args=(self.project.slug,)),
             {'status_code': 302}),
            
            (reverse('ProjectDetail', args=(self.project.slug,)),
             {'status_code': 302}),
            
            (reverse('ApproveProjects'),
             {'status_code': 302}),
            
            (reverse('MyProjects'),
             {'status_code': 302}),

            (reverse('Bookmark_Project', args=(self.project.slug,)),
             {'status_code': 302}),

            (reverse('Unbookmark_Project', args=(self.project.slug,)),
             {'status_code':302}),

            (reverse('ReportUpload', args=(self.project.slug,)),
             {'status_code':302}),

            (reverse('haystack_search'),
             {'status_code':200}),


            #this doesn't work right now.
            #(reverse('serve_file', kwargs={'filename':""}),
            # {'status_code':302}),
        )
        self._test_urls(URLS)


    def tearDown(self):
        self.project.delete()



class TestAdmin(DemoTestCase):
  
    def test_admin(self):
        self.create_user('super', super=True)
        self.login('super')
        #NOTE ProjectSisters is not included due to "no _meta" error??
        self._test_admin((Project, Report, Milestone, TL_ProjType, TL_Database,
                          ProjectMilestones, Family))
