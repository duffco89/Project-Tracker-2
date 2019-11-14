# from django.contrib.auth.models import User, Group
from django.urls import reverse
from django_webtest import WebTest

from pjtk2.tests.factories import *

# import datetime
# import pytz


class MessagesRenderTestCase(WebTest):
    """when each of the users logs into MyProjects, they should see a form
    that contains the project name, project code, and message that the
    project has been "Submitted".  Elaine should not have any
    messages.

    """

    def setUp(self):
        """for these tests, we need a project, some milestones, a project
        lead, a supervisor, a dba, a watcher and an emplpoyee who is
        on the sidelines and shouldn't recieve any messages.
        """

        self.user1 = UserFactory(
            first_name="Jerry", last_name="Seinfield", username="jseinfield"
        )

        self.user2 = UserFactory(
            first_name="George", last_name="Costanza", username="gcostanza"
        )

        self.user3 = UserFactory(
            first_name="Cosmo", last_name="Kramer", username="ckramer"
        )

        self.user4 = UserFactory(
            first_name="Elaine", last_name="Benis", username="ebenis"
        )

        # now setup employee relationships
        # jerry has no boss
        self.employee1 = EmployeeFactory(user=self.user1)
        # George works for Jerry and will be our dba
        self.employee2 = EmployeeFactory(user=self.user2, supervisor=self.employee1)
        # Kramer works for Jerry
        self.employee3 = EmployeeFactory(user=self.user3, supervisor=self.employee1)
        # Elaine works for Kramer
        self.employee4 = EmployeeFactory(user=self.user4, supervisor=self.employee3)

        # we need a milestone to associate the message with
        self.milestone1 = MilestoneFactory.create(
            label="Submitted", category="Core", order=1, report=False
        )

        self.milestone1 = MilestoneFactory.create(
            label="Approved", category="Core", order=2, report=False
        )

        # we need a milestone to associate the message with
        self.milestone2 = MilestoneFactory.create(
            label="Completed", category="Core", order=3, report=False
        )

        # now create a project with an owner and dba.
        self.prj_cd = "LHA_IA12_111"
        self.prj_nm = "Project with messages"

        self.project1 = ProjectFactory.create(
            prj_cd=self.prj_cd, prj_nm=self.prj_nm, owner=self.user3, dba=self.user2
        )

    def test_messages_render_user1(self):
        """user1 is Jerry - he's Kramer's boss and should get
        notification that the project was submitted.
        """
        myuser = self.user1

        login = self.client.login(username=myuser.username, password="Abcd1234")
        self.assertTrue(login)
        response = self.app.get(reverse("MyProjects"), user=myuser)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pjtk2/my_projects.html")

        # jerry notices should contain the new project, the project
        # code and the word submitted
        self.assertContains(response, self.project1.prj_cd)
        self.assertContains(response, self.project1.prj_nm)
        self.assertContains(response, "Submitted")
        # mark the notice as read and submit the form
        form = response.forms["notices"]
        form["form-0-read"].checked = True
        response = form.submit().follow()

        # the response should NOT contain those elements now
        self.assertTemplateUsed(response, "pjtk2/my_projects.html")
        self.assertNotContains(response, self.project1.prj_cd)
        self.assertNotContains(response, self.project1.prj_nm)

    def test_messages_render_user2(self):
        """user2 is george - he's the dba and should get notification that the
        project was submitted and should be able to mark them as read.
        Once read, the messages will no longer appear in the list of
        notices.
        """
        myuser = self.user2

        login = self.client.login(username=myuser.username, password="Abcd1234")
        self.assertTrue(login)
        response = self.app.get(reverse("MyProjects"), user=myuser)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pjtk2/my_projects.html")

        # George's notices should contain the new project, the project
        # code and the word submitted
        self.assertContains(response, self.project1.prj_cd)
        self.assertContains(response, self.project1.prj_nm)
        self.assertContains(response, "Submitted")
        # mark the notice as read and submit the form
        form = response.forms["notices"]
        form["form-0-read"].checked = True
        response = form.submit().follow()

        # the response should NOT contain those elements now
        self.assertTemplateUsed(response, "pjtk2/my_projects.html")
        self.assertNotContains(response, self.project1.prj_cd)
        self.assertNotContains(response, self.project1.prj_nm)

    def test_messages_render_user3(self):
        """user3 is Kramer - he's the project lead and should get notification
        that the project was submitted and should be able to mark the notices
        as read.  Once read, the messages will no longer appear in the
        list of notices.

        """
        myuser = self.user3

        login = self.client.login(username=myuser.username, password="Abcd1234")
        self.assertTrue(login)
        response = self.app.get(reverse("MyProjects"), user=myuser)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pjtk2/my_projects.html")

        # Kramer's notices should contain the new project, the project
        # code and the word submitted
        self.assertContains(response, self.project1.prj_cd)
        self.assertContains(response, self.project1.prj_nm)
        self.assertContains(response, "Submitted")
        # mark the notice as read and submit the form
        form = response.forms["notices"]
        form["form-0-read"].checked = True
        response = form.submit().follow()

        # the response should NOT contain those elements now
        self.assertTemplateUsed(response, "pjtk2/my_projects.html")
        self.assertNotContains(response, self.project1.prj_cd)
        self.assertNotContains(response, self.project1.prj_nm)

    def test_messages_render_user4(self):
        """user4 is Elaine - she isn't a dba, a manager or project lead.  She
        should not recieve any notices about the project.
        """
        myuser = self.user4

        login = self.client.login(username=myuser.username, password="Abcd1234")
        self.assertTrue(login)
        response = self.app.get(reverse("MyProjects"), user=myuser)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pjtk2/my_projects.html")
        self.assertNotContains(response, self.project1.prj_cd)
        self.assertNotContains(response, self.project1.prj_nm)

    def tearDown(self):

        self.project1.delete()
        self.milestone1.delete()
        self.milestone2.delete()

        self.employee1.delete()
        self.employee2.delete()
        self.employee3.delete()

        self.user1.delete()
        self.user2.delete()
        self.user3.delete()
