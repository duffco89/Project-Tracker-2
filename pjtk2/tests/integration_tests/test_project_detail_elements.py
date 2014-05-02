'''=============================================================
~/pjtk2/pjtk2/tests/integration_tests/test_project_detail_elements.py
Created: 01 May 2014 07:10:04


DESCRIPTION:

The tests in this file verify that the elements that depend on a
user's role or the status of the project on the project detail page
render properly.

These elements include buttons/links to:
+ upload reports
+ upload associated files
+ edit information
+ change reporting
+ approve
+ unnapprove
+ signoff

which of these elements are included on the rendered page differ
depending on whether you are a user, the project lead, a manager or a
superuser.

A. Cottrill
=============================================================

'''


from django.core.urlresolvers import reverse
from django.test.client import Client

import pytest
from pjtk2.tests.pytest_fixtures import *

from pjtk2.tests.factories import *


@pytest.mark.django_db
def test_manager_has_correct_project_detail_buttons(client, project, manager):
        ''' managers should have buttons that will enable them to:
              + upload reports
              + upload associated files
              + edit information
              + change reporting
              + approve
              + unnapprove
              + signoff
        '''

        project.approve()
        assert project.is_approved() == True

        login = client.login(username=manager.username,
                                  password='Abcd1234')
        assert login == True

        response = client.get(reverse('project_detail',
                                           kwargs={'slug':project.slug}),)
        response = str(response)

        linkstring_base = '<a href="{0}"'

        #can edit
        url = reverse('EditProject', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response
        
        #can edit
        url = reverse('SisterProjects', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response

        #can edit
        url = reverse('ReportUpload', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response

        #manager only:
        url = reverse('Reports', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response

        #manager only:
        url = reverse('unapprove_project', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response

        #manager only:
        url = reverse('signoff_project', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response

        #can edit
        url = reverse('associated_file_upload', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response
              

@pytest.mark.django_db
def test_manager_unapproved_project_detail_buttons(client, project, manager):
        '''This is an edge case - if the project is approved, a manager should
        have a link that allows them to unapprove it.
        '''

        assert project.is_approved() == False

        login = client.login(username=manager.username,
                                  password='Abcd1234')
        assert login == True

        response = client.get(reverse('project_detail',
                                           kwargs={'slug':project.slug}),)
        response = str(response)

        linkstring_base = '<a href="{0}"'

        #can edit
        url = reverse('approve_project', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response

@pytest.mark.django_db
def test_manager_completed_project_detail_buttons(client, project, manager):
        ''' 'Signoff' project should not appear on completed projects
        '''

        project.signoff()
        assert project.is_complete() == True

        login = client.login(username=manager.username,
                                  password='Abcd1234')
        assert login == True

        response = client.get(reverse('project_detail',
                                           kwargs={'slug':project.slug}),)
        response = str(response)

        linkstring_base = '<a href="{0}"'

        #can edit
        url = reverse('signoff_project', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring not in response


        
@pytest.mark.django_db
def test_project_lead_has_correct_project_detail_buttons(client, project, user):
        '''For the project lead, the project detail should have buttons that
        will them to:
              + upload reports
              + upload associated files
              + edit information
        but not:
              + change reporting
              + approve
              + unnapprove
              + signoff

        '''


        project.approve()
        assert project.is_approved() == True

        login = client.login(username=user.username,
                                  password='Abcd1234')
        assert login == True
        response = client.get(reverse('project_detail',
                                           kwargs={'slug':project.slug}),)

        response = str(response)

        linkstring_base = '<a href="{0}"'

        #can edit
        url = reverse('EditProject', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response
        
        #can edit
        url = reverse('SisterProjects', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response

        #can edit
        url = reverse('ReportUpload', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response

        #manager only:
        url = reverse('Reports', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring not in response

        #manager only:
        url = reverse('unapprove_project', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring not in response

        #manager only:
        url = reverse('signoff_project', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring not in response

        #can edit
        url = reverse('associated_file_upload', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response
              

@pytest.mark.django_db
def test_dba_has_correct_project_detail_buttons(client, project, dba):
        '''For a dba (or superuser), the project detail should have buttons that
        will them to:
              + upload reports
              + upload associated files
              + edit information
        but not:
              + change reporting
              + approve
              + unnapprove
              + signoff
        '''

        project.approve()
        assert project.is_approved() == True
        assert dba.is_superuser==True

        login = client.login(username=dba.username,
                                  password='Abcd1234')
        assert login == True
        response = client.get(reverse('project_detail',
                                           kwargs={'slug':project.slug}),)
        response = str(response)
        linkstring_base = '<a href="{0}"'

        #can edit
        url = reverse('EditProject', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response
        
        #can edit
        url = reverse('SisterProjects', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response

        #can edit
        url = reverse('ReportUpload', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response

        #manager only:
        url = reverse('Reports', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring not in response

        #manager only:
        url = reverse('unapprove_project', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring not in response

        #manager only:
        url = reverse('signoff_project', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring not in response

        #can edit
        url = reverse('associated_file_upload', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring in response




@pytest.mark.django_db
def test_joe_user_has_correct_project_detail_buttons(client, project, joe_user):
        '''For a user is not the proejct lead, the project detail should not
        have buttons that will them to:
              + upload reports
              + upload associated files
              + edit information
              + change reporting
              + approve
              + unnapprove
              + signoff
        '''

        login = client.login(username=joe_user.username,
                                  password='Abcd1234')
        assert login == True
        response = client.get(reverse('project_detail',
                                           kwargs={'slug':project.slug}),)
        response = str(response)
        linkstring_base = '<a href="{0}"'

        #can edit
        url = reverse('EditProject', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring not in response
        
        #can edit
        url = reverse('SisterProjects', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring not in response

        #can edit
        url = reverse('ReportUpload', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring not in response

        #manager only:
        url = reverse('Reports', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring not in response

        #manager only:
        url = reverse('unapprove_project', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring not in response

        #manager only:
        url = reverse('signoff_project', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring not in response

        #can edit
        url = reverse('associated_file_upload', kwargs={'slug':project.slug})
        linkstring = linkstring_base.format(url)
        assert linkstring not in response

