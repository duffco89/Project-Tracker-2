from django.core.urlresolvers import reverse
from django_webtest import WebTest
#from testfixtures import compare
from pjtk2.tests.factories import *


class IndexViewTestCase(WebTest):
    '''verfiy that we can view the site index page'''
    def test_index(self):
        response = self.app.get('')
        assert response.status_int == 200
        self.assertTemplateUsed(response, 'index.html')
        assert 'Site Index' in response
        assert 'Project List' in response        
        assert 'Approved Project List' in response                
        assert 'Approve Projects' in response                        

class SisterFormTestCase(WebTest):

    def setUp(self):
        '''we will need three projects with easy to rember project codes'''
        self.user = UserFactory(username = 'hsimpson',
                                first_name = 'Homer',
                                last_name = 'Simpson')
       
        self.ProjType = ProjTypeFactory()
        self.ProjType2 = ProjTypeFactory(Project_Type = "Nearshore Index")
        
        self.project1 = ProjectFactory.create(PRJ_CD="LHA_IA12_111",
                                              Owner=self.user,
                                              ProjectType = self.ProjType)
        self.project2 = ProjectFactory.create(PRJ_CD="LHA_IA12_222",
                                              Owner=self.user,
                                              ProjectType = self.ProjType)
        self.project3 = ProjectFactory.create(PRJ_CD="LHA_IA12_333",
                                              Owner=self.user,
                                              ProjectType = self.ProjType)

        #same project type, but not approved
        self.project4 = ProjectFactory.create(PRJ_CD="LHA_IA12_444",
                                              Owner=self.user,
                                              ProjectType = self.ProjType, Approved=False)

        #approved, different project type
        self.project5 = ProjectFactory.create(PRJ_CD="LHA_IA12_555",
                                              Owner=self.user,
                                              ProjectType = self.ProjType2)
        #approved, same project type, different year
        self.project6 = ProjectFactory.create(PRJ_CD="LHA_IA11_666",
                                              Owner=self.user,
                                              ProjectType = self.ProjType)


    def test_projectlist(self):

        response = self.app.get(reverse('ProjectList'), user=self.user)
        assert response.status_int == 200
        self.assertTemplateUsed(response, 'ProjectList.html')

        
        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                     args=(self.project3.slug,)), self.project3.PRJ_CD)
        linkstring in response

    def test_sisterbtn(self):
        '''from the details pages, verify that the sisters button
        works and takes us to the sister project page for this
        project.'''

        url = reverse('ProjectDetail', args = (self.project1.slug,))                     
        response = self.app.get(url, user = self.user)

        assert response.status_int == 200
        self.assertTemplateUsed(response, 'projectdetail.html')

        #verify that the sister projects button exists
        linkstring= '<a href="%s"' % reverse('SisterProjects', args = (self.project1.slug,))
        assert linkstring in response

        response = response.click("Sister Projects")

        #if we click on it, verify that we are re-directed to the correct page
        # 'SisterProjects.html' (for this project)
        assert response.status_int == 200
        self.assertTemplateUsed(response, 'SisterProjects.html')

        #verify that the page contains:
        #"Sister projects for:"
        assert "Sister projects for:" in response
        # and self.project1.PRJ_CD
        assert self.project1.PRJ_CD in response
  

    def test_sisterlist_nosisters(self):
        '''the sister project page for a project with two candidates, none selected.'''
        #starting out at the sister project page for project1

        url = reverse('SisterProjects', args = (self.project1.slug,))                     
        response = self.app.get(url, user = self.user)

        assert response.status_int == 200
        self.assertTemplateUsed(response, 'SisterProjects.html')

        assert "Sister projects for:" in response
        
        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                             args = (self.project2.slug,)), self.project2.PRJ_CD)
        #print response
        print "linkstring = %s" % linkstring
        assert linkstring in response
        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                             args=(self.project3.slug,)), self.project3.PRJ_CD)
        assert linkstring in response

        form = response.form
        #there should be two forms in the formset (these form elements end with -sister)
        formcnt = len([x for x in form.fields.keys() if x.endswith("-sister")])
        #print "formcnt = %s" % formcnt
        self.assertEquals(formcnt, 2)
        
        #the check boxes in both should == None
        self.assertEquals(form.fields['form-0-sister'][0].value, None)
        self.assertEquals(form.fields['form-1-sister'][0].value, None)

        #make sure that the projects that should be candidates or
        #sisters aren't in the response
        self.assertNotIn(self.project4.PRJ_CD, response)
        self.assertNotIn(self.project5.PRJ_CD, response)
        self.assertNotIn(self.project6.PRJ_CD, response)




    def test_sisterlist_onesister(self):
        '''the sister project page for a project with one candidate,
        one sister already selected.'''

        self.project1.add_sister(self.project2.slug)

        url = reverse('SisterProjects', args = (self.project1.slug,))                     
        response = self.app.get(url, user = self.user)

        assert response.status_int == 200
        self.assertTemplateUsed(response, 'SisterProjects.html')

        assert "Sister projects for:" in response
        
        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                             args = (self.project2.slug,)), self.project2.PRJ_CD)

        assert linkstring in response
        linkstring= '<a href="%s">%s</a>' % (reverse('ProjectDetail', 
                             args=(self.project3.slug,)), self.project3.PRJ_CD)
        assert linkstring in response

        form = response.form
        #there should be two forms in the formset (these form elements end with -sister)
        formcnt = len([x for x in form.fields.keys() if x.endswith("-sister")])
        #print "formcnt = %s" % formcnt
        self.assertEquals(formcnt, 2)
        
        #the check boxes in both should == None
        self.assertEquals(form.fields['form-0-sister'][0].value, 'on')
        self.assertEquals(form.fields['form-1-sister'][0].value, None)

        #make sure that the projects that should be candidates or
        #sisters aren't in the response
        self.assertNotIn(self.project4.PRJ_CD, response)
        self.assertNotIn(self.project5.PRJ_CD, response)
        self.assertNotIn(self.project6.PRJ_CD, response)


    def test_sisterlist_nocandidates(self):
        '''the sister project page for a project without any
        candidates should not produce a form, but should present a
        meaningful message noting that there are no candidates
        currenly.  This test cases runs through scenarios with an
        unapproved project, a project of a differnt type and a project
        in a different year.'''

        url = reverse('SisterProjects', args = (self.project4.slug,))                     
        response = self.app.get(url, user = self.user)

        assert response.status_int == 200
        self.assertTemplateUsed(response, 'SisterProjects.html')

        assert "Sister projects for:" in response

        msg = "There are currently no comperable projects for %s" % self.project4.PRJ_CD
        self.assertIn(msg, response)

        #make sure that the projects that should not be candidates or
        #sisters aren't in the response
        self.assertNotIn(self.project1.PRJ_CD, response)
        self.assertNotIn(self.project2.PRJ_CD, response)
        self.assertNotIn(self.project3.PRJ_CD, response)
        self.assertNotIn(self.project5.PRJ_CD, response)
        self.assertNotIn(self.project6.PRJ_CD, response)

        #Differnt Project Type
        url = reverse('SisterProjects', args = (self.project5.slug,))                     
        response = self.app.get(url, user = self.user)

        assert response.status_int == 200
        self.assertTemplateUsed(response, 'SisterProjects.html')

        assert "Sister projects for:" in response

        msg = "There are currently no comperable projects for %s" % self.project5.PRJ_CD
        self.assertIn(msg, response)

        #make sure that the projects that should not be candidates or
        #sisters aren't in the response
        self.assertNotIn(self.project1.PRJ_CD, response)
        self.assertNotIn(self.project2.PRJ_CD, response)
        self.assertNotIn(self.project3.PRJ_CD, response)
        self.assertNotIn(self.project4.PRJ_CD, response)
        self.assertNotIn(self.project6.PRJ_CD, response)

        #approved project, different year
        url = reverse('SisterProjects', args = (self.project6.slug,))                     
        response = self.app.get(url, user = self.user)

        assert response.status_int == 200
        self.assertTemplateUsed(response, 'SisterProjects.html')

        assert "Sister projects for:" in response

        msg = "There are currently no comperable projects for %s" % self.project6.PRJ_CD
        self.assertIn(msg, response)

        #make sure that the projects that should not be candidates or
        #sisters aren't in the response
        self.assertNotIn(self.project1.PRJ_CD, response)
        self.assertNotIn(self.project2.PRJ_CD, response)
        self.assertNotIn(self.project3.PRJ_CD, response)
        self.assertNotIn(self.project4.PRJ_CD, response)
        self.assertNotIn(self.project5.PRJ_CD, response)



    def test_add_remove_sisters(self):
        '''this test will test the whold process.  We will log into
        the lister list, click on a sister, submit the form, return to
        the sister page, verify that the sister is selected, unselect
        it and re-sumbit the form.  Finally retrun to the list of
        sisters and verify that no sisters are selected.'''

        #we will log into the lister list, click on a sister, 
        url = reverse('SisterProjects', args = (self.project1.slug,))                     
        response = self.app.get(url, user = self.user)

        assert response.status_int == 200
        self.assertTemplateUsed(response, 'SisterProjects.html')
        form = response.form
        #there should be two forms in the formset (these form elements end with -sister)
        formcnt = len([x for x in form.fields.keys() if x.endswith("-sister")])
        #print "formcnt = %s" % formcnt
        self.assertEquals(formcnt, 2)
        
        #the check boxes in both should == None
        self.assertEquals(form.fields['form-0-sister'][0].value, None)
        self.assertEquals(form.fields['form-1-sister'][0].value, None)
        
        #check one of the boxes and submit the form, 
        form.fields['form-0-sister'][0].value = 'on'
        form.submit()        

        proj = Project.objects.get(slug=self.project1.slug)
        sisters = proj.get_sisters()
        self.assertEqual(len(sisters),1)
        self.assertEqual(sisters[0].PRJ_CD,self.project2.PRJ_CD)

        #========================
        #return to the sister page, 
        url = reverse('SisterProjects', args = (self.project1.slug,))                     
        response = self.app.get(url, user = self.user)
        assert response.status_int == 200

        form = response.form        

        #verify that the sister is selected, 
        self.assertEquals(form.fields['form-0-sister'][0].value, 'on')
        self.assertEquals(form.fields['form-1-sister'][0].value, None)

        #unselect it and re-sumbit the form.  
        form.fields['form-0-sister'][0].value = None
        form.submit()        

        proj = Project.objects.get(slug=self.project1.slug)
        sisters = proj.get_sisters()
        self.assertEqual(len(sisters),0)


        #======================== 
        # retuRn to the list of sisters one final time and verify that
        # no sisters are selected

        url = reverse('SisterProjects', args = (self.project1.slug,))                     
        response = self.app.get(url, user = self.user)

        assert response.status_int == 200
        self.assertTemplateUsed(response, 'SisterProjects.html')
        form = response.form
        #there should be two forms in the formset (these form elements end with -sister)
        formcnt = len([x for x in form.fields.keys() if x.endswith("-sister")])
        #print "formcnt = %s" % formcnt
        self.assertEquals(formcnt, 2)
        
        #the check boxes in both should == None
        self.assertEquals(form.fields['form-0-sister'][0].value, None)
        self.assertEquals(form.fields['form-1-sister'][0].value, None)



    def test_disown_sister(self):
        '''.'''

        self.project1.add_sister(self.project2.slug)
        self.project1.add_sister(self.project3.slug)

        proj = Project.objects.get(slug=self.project1.slug)
        sisters = proj.get_sisters()
        self.assertEqual(len(sisters),2)
        self.assertEqual(sisters[0].PRJ_CD,self.project2.PRJ_CD)
        self.assertEqual(sisters[1].PRJ_CD,self.project3.PRJ_CD)

        #we will log into the lister list, click on a sister, 
        url = reverse('SisterProjects', args = (self.project1.slug,))                     
        response = self.app.get(url, user = self.user)

        assert response.status_int == 200
        self.assertTemplateUsed(response, 'SisterProjects.html')
        form = response.form
        #there should be two forms in the formset 
        formcnt = len([x for x in form.fields.keys() if x.endswith("-sister")])
        #print "formcnt = %s" % formcnt
        self.assertEquals(formcnt, 2)
        
        #the check boxes in both should == None
        self.assertEquals(form.fields['form-0-sister'][0].value, 'on')
        self.assertEquals(form.fields['form-1-sister'][0].value, 'on')
        
        #uncheck both of the boxes and submit the form, 
        form.fields['form-0-sister'][0].value = None
        form.fields['form-1-sister'][0].value = None
        form.submit()        

        #project 1 shouldn't have any sisters now
        proj = Project.objects.get(slug=self.project1.slug)
        sisters = proj.get_sisters()
        self.assertEqual(len(sisters),0)

        #project 2 should have just one sister - project 3
        proj = Project.objects.get(slug=self.project2.slug)
        sisters = proj.get_sisters()
        self.assertEqual(len(sisters),1)
        self.assertEqual(sisters[0].PRJ_CD,self.project3.PRJ_CD)

        #Likewise project 3 should have just one sister - project 2
        proj = Project.objects.get(slug=self.project3.slug)
        sisters = proj.get_sisters()
        self.assertEqual(len(sisters),1)
        self.assertEqual(sisters[0].PRJ_CD,self.project2.PRJ_CD)






    def tearDown(self):
        self.project1.delete()
        self.project2.delete()
        self.project3.delete()        
        self.user.delete()
        
