from django.core.urlresolvers import reverse
import pytest
from .factories import *
from pprint import pprint

from pytest_fixtures import *

@pytest.mark.django_db
def test_anon_user_cannot_approve_project(client, project):
        '''An anonymous user should not be able to approve projects.  If they
        try to access the page, they should be re-directed to the login
        page.'''

        assert project.is_approved()==False
        assert client.login() == False
        response = client.get(reverse('approve_project',
                                           kwargs={'slug':project.slug}))
        #verify that we're redirected to login page
        assert response.status_code == 302
        url = reverse('login').strip('/')
        assert url in response['Location']
        assert project.is_approved()==False


@pytest.mark.django_db
def test_anon_user_cannot_unapprove_project(client, project):
        '''An anonymous user should not be able to approve projects.  If they
        try to access the unapprove page directly, they should be
        re-directed to the login page and the project will remain unapproved.

        '''

        project.approve()
        assert project.is_approved() == True

        response = client.get(reverse('unapprove_project',
                                           kwargs={'slug':project.slug}),)
                              #follow=True)
        assert client.login() == False

        assert response.status_code == 302
        url = reverse('login').strip('/')
        assert url in response['Location']
        assert project.is_approved() == True


@pytest.mark.django_db
def test_anon_user_cannot_signoff_project(client, project):
        '''An anonymous user should not be able to signoff on a project.  If
        they try to access the signoff page, they should be
        re-directed to the login page.

        '''

        assert project.is_complete() == False

        response = client.get(reverse('signoff_project',
                                           kwargs={'slug':project.slug}))
        #verify that we're redirected to login page
        assert response.status_code == 302
        url = reverse('login').strip('/')
        assert url in response['Location']

        assert project.is_complete() == False
