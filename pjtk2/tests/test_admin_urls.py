'''Some tests to quickly verify that all of the urls work and
that the admin contains interfaces to the models that we need.'''

from pjtk2.tests import DemoTestCase
from django.core.urlresolvers import reverse
from pjtk2.tests.factories import *
from django.db.models.signals import pre_save, post_save




def setup():
    '''disconnect the signals before each test - not needed here'''
    pre_save.disconnect(send_notice_prjms_changed, sender=ProjectMilestones)

def teardown():
    '''re-connecct the signals here.'''
    pre_save.disconnect(send_notice_prjms_changed, sender=ProjectMilestones)



class TestUrls(DemoTestCase):

    def setUp(self):

        #PROJECT
        self.project = ProjectFactory.create(prj_cd="LHA_IA12_111")
        self.tag = 'tag'
        self.project.tags.add(self.tag)

    def test_urls(self):
        '''Verify that all of the pages exist.  Can't use template_used
        because all views require login.  They are re-directed to the
        login'''
        URLS = (

            (reverse('login'),
             {'status_code':200}),

            (reverse('logout'),
             {'status_code':200}),

            (reverse('ProjectList'),
             {'status_code': 200}),

            (reverse('ProjectList_q'),
             {'status_code': 200}),

            (reverse('haystack_search'),
             {'status_code':200}),

            (reverse('project_detail', args=(self.project.slug,)),
             {'status_code':200}),

            (reverse('TaggedProjects',args=(self.tag,)),
             {'status_code':200}),

            (reverse('project_tag_list'),
             {'status_code':200}),

            (reverse('find_projects_roi'),
             {'status_code':200}),

            (reverse('about_view'),
             {'status_code':200}),


            #the remaining views all require login:

            (reverse('NewProject'),
             {'status_code': 302}),

            (reverse('CopyProject', args=(self.project.slug,)),
             {'status_code': 302}),

            (reverse('EditProject', args=(self.project.slug,)),
             {'status_code': 302}),

            (reverse('ApproveProjects'),
             {'status_code': 302}),

            (reverse('signoff_project', args=(self.project.slug,)),
             {'status_code': 302}),

            (reverse('MyProjects'),
             {'status_code': 302}),

            (reverse('Bookmark_Project', args=(self.project.slug,)),
             {'status_code': 302}),

            (reverse('Unbookmark_Project', args=(self.project.slug,)),
             {'status_code':302}),

            (reverse('ReportUpload', args=(self.project.slug,)),
             {'status_code':302}),

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
        self._test_admin((Project, Report, Milestone, ProjectType, Database,
                          ProjectMilestones, Family))
