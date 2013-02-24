"""
functional tests of the new project form.
Adapted from the examples described here:
http://www.tdd-django-tutorial.com/tutorial/1/

Usage: python manage.py tests fct

Currently there are tests to ensure that we can see project list,
project info and fill project form in with valid data.

TODO: test for:
- bad data (malform project code, missing elements, wrong dates,
  inconsistent dates,, duplicate project codes.)

NOTE - these tests are currently incomplete.  I can't figure out how
to get selenium to redirect after a form has been subitted - it
continually returns a server error.
  
"""

from django.test import LiveServerTestCase
from selenium import webdriver
from datetime import datetime

from pjtk2.tests.factories import *

import pdb


class ProjectTest(LiveServerTestCase):

    def fill_in_project(self, project_info):
        '''A helper function to fill in project form fields depending
        on the values in project_info'''

        project_name_field = self.browser.find_element_by_name('PRJ_NM')
        project_name_field.send_keys(project_info.PRJ_NM)

        project_code_field = self.browser.find_element_by_name('PRJ_CD')
        project_code_field.send_keys(project_info.PRJ_CD)

        project_lead_field = self.browser.find_element_by_name('PRJ_LDR')
        project_lead_field.send_keys(project_info.PRJ_LDR)

        project_desc_field = self.browser.find_element_by_name('COMMENT')
        project_desc_field.send_keys(project_info.COMMENT)

        #pdb.set_trace()
        
        project_start_field = self.browser.find_element_by_name('PRJ_DATE0')
        startdate = project_info.PRJ_DATE0.strftime("%m/%d/%Y")
        project_start_field.send_keys(startdate)

        project_end_field = self.browser.find_element_by_name('PRJ_DATE1')
        enddate = project_info.PRJ_DATE1.strftime("%m/%d/%Y")
        project_end_field.send_keys(enddate)

        #self.browser.find_element_by_name('ProjType').click()
        #pdb.set_trace()
        ProjectType= project_info.ProjectType.Project_Type

        el = self.browser.find_element_by_id('id_ProjectType')
        for option in el.find_elements_by_tag_name('option'):
            if option.text == ProjectType:
                option.click() 

        el = self.browser.find_element_by_id('id_MasterDatabase')
        MasterDatabase = project_info.MasterDatabase.MasterDatabase
        
        for option in el.find_elements_by_tag_name('option'):
            if option.text == MasterDatabase:
                option.click() 

        return self
    
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

        #create some data elsements:
        ProjTypeFactory.create()
        DatabaseFactory.create()
        ProjectFactory.create()


    def tearDown(self):
        self.browser.quit()


    def test_start_at_index(self):
        
        #bob opens the browser and navigates to the new project page:
        self.browser.get(self.live_server_url + "/")

        #make sure the project code is on this page
        header = self.browser.find_element_by_tag_name('h1')                
        self.assertIn('Site Index', header.text)    

        link = self.browser.find_element_by_link_text("Project List").click()

        self.browser.implicitly_wait(4)

        header = self.browser.find_element_by_tag_name('h1')                
        self.assertIn('Projects', header.text)   
         
        #find a project link and click on it too:
        link = self.browser.find_element_by_link_text("LHA_IA12_123").click()
        pdb.set_trace()

        
    def test_view_project_list(self):
        '''Verify that we can see the list of projects (there will be
        only in the test database)'''
        #bob opens the browser and navigates to the new project page:
        self.browser.get(self.live_server_url + "/test/projects/")

        #there should be a heading stating what the form is for:
        heading = self.browser.find_element_by_tag_name('h1')                
        body = self.browser.find_element_by_tag_name('body')                        
        self.assertIn('Projects', heading.text)        
        self.assertIn('LHA_IA12_123', body.text)        
        self.assertIn('Create a new project', body.text)                

    def test_view_project_Info(self):
        '''verify that we can view the project information page and that
        the expected elements are there'''
         
        PRJ_CD = "LHA_IA12_123"
        
        #bob opens the browser and navigates to the new project page:
        url = "/test/viewreports/%s/" % PRJ_CD.lower()
        self.browser.get(self.live_server_url + url)

        heading = self.browser.find_element_by_tag_name('h1')                
        self.assertIn('UGLMU Project', heading.text)        

        heading = self.browser.find_elements_by_tag_name('h2')                
        self.assertIn('Project Information', heading[0].text)        
        self.assertIn('Reporting Requirements', heading[1].text)
        
        #make sure the project we just entered in on this page:                
        body = self.browser.find_element_by_tag_name('body')                
        self.assertIn('Project Code: %s' % PRJ_CD , body.text)        
        self.assertIn('Project Name:', body.text)        
        self.assertIn('Project Lead:', body.text)        
        self.assertIn('Project Type:', body.text)        
        self.assertIn('Master Database:', body.text)                        
                        
    def test_can_create_new_project(self):
        #bob opens the browser and navigates to the new project page:
        self.browser.get(self.live_server_url + "/test/newproject/")

        #there should be a heading stating what the form is for:
        heading = self.browser.find_element_by_tag_name('h1')                
        self.assertIn('New Project', heading.text)        

        #fill in the project forms with good data:
        PRJ_CD="LHA_IA12_111"
        project_info = ProjectFactory.build(PRJ_CD=PRJ_CD)
        self.fill_in_project(project_info)
                
        #self.browser.find_element_by_id('submit-id-submit').click()
        
        submit = 'input[type="submit"]'
        submit = self.browser.find_element_by_css_selector(submit)
        submit.click()        
        
        self.browser.implicitly_wait(4)


        #THIS DOES NOT WORK - SELENIUM WILL NOT RE-DIRECT TO INFO PAGE!
        # we should now be redirected to the proejct information page
        #for the project we just entered:
        #pdb.set_trace()
##        heading = self.browser.find_element_by_tag_name('h1')                
##        self.assertIn('UGLMU Project', heading.text)        
##
##        heading = self.browser.find_elements_by_tag_name('h2')                
##        self.assertIn('Project Information', heading.text[0])        
##        self.assertIn('Reporting Requirements', heading.text[1])
##        
##        #make sure the project we just entered in on this page:                
##        body = self.browser.find_element_by_tag_name('body')                
##        self.assertIn('Project Code: %s' % PRJ_CD , body)        
        

#   self.fail("finish the test")


    def test_can_update_project(self):
        
        PRJ_CD = "LHA_IA12_123"
        #bob opens the browser and navigates to the new project page:
        url = "/test/viewreports/%s/" % PRJ_CD.lower()

        #bob opens the browser and navigates to the new project page:
        self.browser.get(self.live_server_url + url)

        #make sure the project code is on this page
        body = self.browser.find_element_by_tag_name('body')                
        self.assertIn('Project Code: %s' % PRJ_CD , body.text)    

        link = self.browser.find_element_by_link_text("Edit Information").click()
        self.browser.implicitly_wait(4)
        
#   self.fail("finish the test")
        

