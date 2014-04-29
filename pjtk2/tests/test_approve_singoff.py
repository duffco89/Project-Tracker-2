from django.core.urlresolvers import reverse
import pytest
from .factories import *
from pprint import pprint

@pytest.fixture(scope="module", autouse=True)
def disconnect_signals():
    '''disconnect the signals before each test - not needed here'''
    pre_save.disconnect(send_notice_prjms_changed, sender=ProjectMilestones)


@pytest.fixture(scope='module')
def user(db):
    """return a normal user named homer
    """
    password = "Abcd1234"
    homer = UserFactory.create(username = 'hsimpson',
                        first_name = 'Homer',
                        last_name = 'Simpson',
                        password = password)
    return(homer)

@pytest.fixture(scope='module')
def project(db, user):

    milestone1 = MilestoneFactory.create(label = "Approved")
    milestone2 = MilestoneFactory.create(label = "Sign Off")

    project = ProjectFactory.create(prj_cd="LHA_IA12_111",
                                          owner=user)
    return(project)



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
